import pytest
from briefagent.tools.html_cleaner import clean_html_to_markdown
from briefagent.tools.manager import ToolManager
from briefagent.tools.resilience import CircuitBreaker, with_retry_and_circuit_breaker
from briefagent.tools.schema_guard import ToolError


@pytest.mark.asyncio
async def test_schema_guard_invalid_url():
    mgr = ToolManager(force_mock=True)
    with pytest.raises(ToolError) as exc_info:
        await mgr.scrape_page("ftp://invalid-protocol.com")
    assert "Must start with https:// or http://" in str(exc_info.value)


@pytest.mark.asyncio
async def test_schema_guard_invalid_search_query():
    mgr = ToolManager(force_mock=True)
    with pytest.raises(ToolError) as exc_info:
        await mgr.web_search(query="")
    assert "ToolError: Invalid argument" in str(exc_info.value)


@pytest.mark.asyncio
async def test_html_cleaner_strips_boilerplate():
    html = """
    <html>
      <head><title>Test Page</title></head>
      <body>
        <nav><a href="/">Home</a></nav>
        <div class="cookie-banner">Accept all cookies</div>
        <h1>Company Mission</h1>
        <p>We build automated infrastructure for data teams.</p>
        <script>console.log('tracker');</script>
        <footer>Copyright 2024</footer>
      </body>
    </html>
    """
    cleaned = clean_html_to_markdown(html)
    assert "Company Mission" in cleaned
    assert "We build automated infrastructure" in cleaned
    assert "Accept all cookies" not in cleaned
    assert "console.log" not in cleaned
    assert "<nav>" not in cleaned


@pytest.mark.asyncio
async def test_retry_and_backoff_recovery():
    fail_count = 0

    async def flaky_api():
        nonlocal fail_count
        fail_count += 1
        if fail_count < 2:
            raise ConnectionError("Network blip")
        return "Recovered data"

    cb = CircuitBreaker(failure_threshold=3)
    decorated = with_retry_and_circuit_breaker(
        max_retries=2,
        base_delay=0.01,
        circuit_breaker=cb,
    )(flaky_api)

    result = await decorated()
    assert result["success"] is True
    assert result["data"] == "Recovered data"
    assert result["retry_count"] == 1
    assert result["recovered"] is True
    assert cb.state == "CLOSED"


@pytest.mark.asyncio
async def test_circuit_breaker_trips():
    async def always_failing_api():
        raise RuntimeError("Fatal server explosion")

    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.2)
    decorated = with_retry_and_circuit_breaker(
        max_retries=0,
        base_delay=0.01,
        circuit_breaker=cb,
    )(always_failing_api)

    # Call 1: fails, failures=1
    res1 = await decorated()
    assert res1["success"] is False
    assert cb.state == "CLOSED"

    # Call 2: fails, failures=2 -> transitions to OPEN
    res2 = await decorated()
    assert res2["success"] is False
    assert cb.state == "OPEN"
    assert cb.can_execute() is False


@pytest.mark.asyncio
async def test_tool_manager_mock_search_and_scrape():
    mgr = ToolManager(force_mock=True)
    search_res = await mgr.web_search("Snowflake platform and scale", num_results=3)
    assert search_res["success"] is True
    assert len(search_res["data"]) >= 1
    assert "Snowflake" in search_res["data"][0]["title"]

    scrape_res = await mgr.scrape_page("https://snowflake.com/about")
    assert scrape_res["success"] is True
    assert "7,200+" in scrape_res["data"]


@pytest.mark.asyncio
async def test_tool_manager_adversarial_dns_lookup():
    mgr = ToolManager(force_mock=True)
    dns_res = await mgr.domain_dns_lookup("omnivortexhypertech.nonexistent")
    assert dns_res["success"] is True
    assert dns_res["data"]["is_live"] is False
    assert dns_res["data"]["has_mx"] is False
