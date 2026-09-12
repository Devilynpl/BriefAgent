import json
from typing import List, Optional
from pydantic import BaseModel


class BenchmarkCompany(BaseModel):
    name: str
    domain: str
    tier: str  # "ENTERPRISE", "MID_MARKET_SAAS", "SMALL_SMB", "ADVERSARIAL_STEALTH"
    is_adversarial: bool = False
    notes: Optional[str] = None


BENCHMARK_25_DATA: List[dict] = [
    # 10 Enterprise / Large companies
    {"name": "Snowflake", "domain": "snowflake.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "Cloud data warehousing, high noise"},
    {"name": "Datadog", "domain": "datadoghq.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "Cloud monitoring and APM platform"},
    {"name": "Stripe", "domain": "stripe.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "Financial infrastructure & payments"},
    {"name": "Cloudflare", "domain": "cloudflare.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "Web security, CDN and edge compute"},
    {"name": "HubSpot", "domain": "hubspot.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "CRM, marketing automation"},
    {"name": "Shopify", "domain": "shopify.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "Global e-commerce platform"},
    {"name": "Twilio", "domain": "twilio.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "Customer engagement and communications APIs"},
    {"name": "Atlassian", "domain": "atlassian.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "Collaboration software (Jira, Confluence)"},
    {"name": "GitLab", "domain": "gitlab.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "DevSecOps platform"},
    {"name": "Asana", "domain": "asana.com", "tier": "ENTERPRISE", "is_adversarial": False, "notes": "Work management and tracking software"},

    # 8 Mid-market B2B SaaS / Software Houses
    {"name": "Monterail", "domain": "monterail.com", "tier": "MID_MARKET_SAAS", "is_adversarial": False, "notes": "Software development company"},
    {"name": "Netguru", "domain": "netguru.com", "tier": "MID_MARKET_SAAS", "is_adversarial": False, "notes": "Digital acceleration & consultancy"},
    {"name": "10Clouds", "domain": "10clouds.com", "tier": "MID_MARKET_SAAS", "is_adversarial": False, "notes": "AI and software development house"},
    {"name": "Brainly", "domain": "brainly.com", "tier": "MID_MARKET_SAAS", "is_adversarial": False, "notes": "EdTech peer-to-peer learning network"},
    {"name": "Docplanner", "domain": "docplanner.com", "tier": "MID_MARKET_SAAS", "is_adversarial": False, "notes": "Healthcare booking and management SaaS"},
    {"name": "PostHog", "domain": "posthog.com", "tier": "MID_MARKET_SAAS", "is_adversarial": False, "notes": "Open-source product analytics suite"},
    {"name": "Supabase", "domain": "supabase.com", "tier": "MID_MARKET_SAAS", "is_adversarial": False, "notes": "Open-source Firebase alternative"},
    {"name": "Basecamp", "domain": "basecamp.com", "tier": "MID_MARKET_SAAS", "is_adversarial": False, "notes": "Project management software by 37signals"},

    # 4 Small / Local SMBs
    {"name": "Boldare", "domain": "boldare.com", "tier": "SMALL_SMB", "is_adversarial": False, "notes": "Digital product design & development"},
    {"name": "Droptica", "domain": "droptica.com", "tier": "SMALL_SMB", "is_adversarial": False, "notes": "Drupal agency & web development agency"},
    {"name": "Apptension", "domain": "apptension.com", "tier": "SMALL_SMB", "is_adversarial": False, "notes": "Creative software house for SaaS & agencies"},
    {"name": "Ideamotive", "domain": "ideamotive.co", "tier": "SMALL_SMB", "is_adversarial": False, "notes": "Tech talent and product development agency"},

    # 3 Adversarial / Phantom / Stealth companies (Zero-hallucination verification)
    {"name": "OmniVortex HyperTech Dynamics", "domain": "omnivortexhypertech.nonexistent", "tier": "ADVERSARIAL_STEALTH", "is_adversarial": True, "notes": "Fictional company, must gracefully degrade"},
    {"name": "Aetheria Quantum BioLabs", "domain": "aetheriaquantumbio.invalid", "tier": "ADVERSARIAL_STEALTH", "is_adversarial": True, "notes": "Fictional deeptech entity, zero sources"},
    {"name": "NonExistentPhantomCorp123", "domain": "nonexistentphantomcorp123.fake", "tier": "ADVERSARIAL_STEALTH", "is_adversarial": True, "notes": "Non-registered ghost company, strict degradation test"},
]


def load_benchmark_25() -> List[BenchmarkCompany]:
    return [BenchmarkCompany(**item) for item in BENCHMARK_25_DATA]
