import re
from typing import Dict, List, Optional


def clean_html_to_markdown(html_content: str) -> str:
    """
    Lightweight, dependency-free HTML-to-clean-text/markdown converter.
    Strips cookie banners, navbars, footers, scripts, styles, and extracts readable text.
    """
    if not html_content:
        return ""

    # Remove script, style, svg, noscript tags
    cleaned = re.sub(r"<(script|style|svg|noscript|header|footer|nav)[^>]*>.*?</\1>", " ", html_content, flags=re.DOTALL | re.IGNORECASE)

    # Remove cookie / consent notices
    cleaned = re.sub(r"<div[^>]*(cookie|consent|banner|popup)[^>]*>.*?</div>", " ", cleaned, flags=re.DOTALL | re.IGNORECASE)

    # Replace headings with markdown
    cleaned = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n# \1\n", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", cleaned, flags=re.DOTALL | re.IGNORECASE)

    # Replace links and paragraphs
    cleaned = re.sub(r"<p[^>]*>(.*?)</p>", r"\n\1\n", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<li[^>]*>(.*?)</li>", r"\n* \1", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)

    # Strip remaining HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)

    # Decode HTML entities
    cleaned = cleaned.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"")

    # Normalize whitespace
    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    return "\n".join(lines)
