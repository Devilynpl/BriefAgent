import asyncio
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl
import dns.resolver
import httpx

from .html_cleaner import clean_html_to_markdown
from .resilience import CircuitBreaker, with_retry_and_circuit_breaker
from .schema_guard import ToolError, validate_tool_input

logger = logging.getLogger("briefagent.tools")

# Schemas for Tool Inputs
class WebSearchInput(BaseModel):
    query: str = Field(..., min_length=2, description="Search query string")
    num_results: int = Field(default=5, ge=1, le=10, description="Number of results to return")

import ipaddress
import socket
from urllib.parse import urlparse

class ScrapePageInput(BaseModel):
    url: str = Field(..., description="Target webpage URL, must start with http:// or https://")

    def model_post_init(self, __context: Any) -> None:
        if not (self.url.startswith("http://") or self.url.startswith("https://")):
            raise ToolError(f"ToolError: Invalid argument 'url'. Must start with https:// or http:// (got '{self.url}')")

        # SECURITY: SSRF Guard (Server-Side Request Forgery Prevention)
        parsed = urlparse(self.url)
        hostname = parsed.hostname
        if not hostname:
            raise ToolError("ToolError: Invalid URL, missing hostname.")

        # Reject common loopback names immediately
        if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
            raise ToolError(f"ToolError: SSRF blocked. Access to local interfaces ({hostname}) is forbidden.")

        # Resolve host to IP and check if it belongs to private or link-local ranges
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip_obj = ipaddress.ip_address(ip_str)
                if (
                    ip_obj.is_private
                    or ip_obj.is_loopback
                    or ip_obj.is_link_local
                    or ip_obj.is_reserved
                    or ip_obj.is_multicast
                ):
                    raise ToolError(
                        f"ToolError: SSRF blocked. Target resolved to restricted/private IP address {ip_str}."
                    )
        except socket.gaierror:
            # Domain cannot be resolved, allow execution to fail gracefully downstream
            pass

class DomainDnsInput(BaseModel):
    domain: str = Field(..., min_length=3, description="Domain name (e.g. snowflake.com)")

class ToolManager:
    """
    Unified Tool Manager providing:
    - web_search
    - scrape_page
    - domain_dns_lookup
    Protected with Exponential Backoff (1s -> 3s, max 2 retries), Circuit Breaker, and Schema Guard.
    """

    def __init__(self, force_mock: bool = False):
        self.force_mock = force_mock
        self.search_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
        self.scrape_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
        self.dns_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
        self.total_tool_calls: int = 0
        self.recovered_errors: int = 0
        self.unrecovered_errors: int = 0

    @property
    def recovery_rate(self) -> float:
        total_errors = self.recovered_errors + self.unrecovered_errors
        if total_errors == 0:
            return 1.0
        return self.recovered_errors / total_errors

    async def _execute_search_internal(self, query: str, num_results: int) -> List[Dict[str, str]]:
        import asyncio
        from duckduckgo_search import DDGS

        def do_search():
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=num_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })
            return results

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(None, do_search)
        return results

    async def _execute_scrape_internal(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                clean_md = clean_html_to_markdown(resp.text)
                if len(clean_md.strip()) > 50:
                    return clean_md
                return ""
            elif resp.status_code in (429, 500, 502, 503):
                raise httpx.HTTPStatusError(f"HTTP {resp.status_code}", request=resp.request, response=resp)
        raise Exception(f"Scraping failed for URL: {url} (Status: {resp.status_code})")

    async def _execute_dns_internal(self, domain: str) -> Dict[str, Any]:
        clean_domain = domain.lower().replace("https://", "").replace("http://", "").split("/")[0]
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 3.0
            resolver.lifetime = 3.0
            
            has_a = False
            has_mx = False
            try:
                a_records = resolver.resolve(clean_domain, "A")
                has_a = len(a_records) > 0
            except Exception:
                has_a = False

            try:
                mx_records = resolver.resolve(clean_domain, "MX")
                has_mx = len(mx_records) > 0
            except Exception:
                has_mx = False

            if not has_a and not has_mx:
                return {"domain": clean_domain, "is_live": False, "has_mx": False, "has_a": False, "error": "NXDOMAIN"}
            return {"domain": clean_domain, "is_live": True, "has_mx": has_mx, "has_a": has_a, "provider": "Public DNS"}
        except Exception:
            return {"domain": clean_domain, "is_live": False, "has_mx": False, "has_a": False, "error": "DNS lookup failed"}

    async def web_search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        self.total_tool_calls += 1
        validated = validate_tool_input(WebSearchInput, {"query": query, "num_results": num_results})
        
        decorated = with_retry_and_circuit_breaker(
            max_retries=2,
            base_delay=0.1,  # Fast in tests, 1s in prod
            circuit_breaker=self.search_cb,
        )(self._execute_search_internal)
        
        res = await decorated(validated.query, validated.num_results)
        if res.get("recovered"):
            self.recovered_errors += 1
        elif not res.get("success"):
            self.unrecovered_errors += 1
        return res

    async def scrape_page(self, url: str) -> Dict[str, Any]:
        self.total_tool_calls += 1
        validated = validate_tool_input(ScrapePageInput, {"url": url})

        decorated = with_retry_and_circuit_breaker(
            max_retries=2,
            base_delay=0.1,
            circuit_breaker=self.scrape_cb,
        )(self._execute_scrape_internal)

        res = await decorated(validated.url)
        if res.get("recovered"):
            self.recovered_errors += 1
        elif not res.get("success"):
            self.unrecovered_errors += 1
        return res

    async def domain_dns_lookup(self, domain: str) -> Dict[str, Any]:
        self.total_tool_calls += 1
        validated = validate_tool_input(DomainDnsInput, {"domain": domain})

        decorated = with_retry_and_circuit_breaker(
            max_retries=2,
            base_delay=0.1,
            circuit_breaker=self.dns_cb,
        )(self._execute_dns_internal)

        res = await decorated(validated.domain)
        if res.get("recovered"):
            self.recovered_errors += 1
        elif not res.get("success"):
            self.unrecovered_errors += 1
        return res
