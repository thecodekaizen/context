"""Search receipts and bounded public-source inspection, not invented citations."""

import hashlib
import ipaddress
import re
import socket
from html.parser import HTMLParser
from typing import ClassVar
from urllib.parse import urlsplit, urlunsplit

import httpx

MEDIA_HOSTS = {
    "images-assets.nasa.gov",
    "svs.gsfc.nasa.gov",
    "upload.wikimedia.org",
    "commons.wikimedia.org",
}
DOCUMENT_DOMAINS = (
    "nasa.gov",
    "esa.int",
    "noaa.gov",
    "usgs.gov",
    "wikipedia.org",
    "wikimedia.org",
    "who.int",
    "cdc.gov",
    "gov.uk",
    "bbc.com",
    "bbc.co.uk",
    "apnews.com",
    "reuters.com",
    "un.org",
    "space.com",
    "planetary.org",
    "theguardian.com",
    "pbs.org",
    "npr.org",
    "smithsonianmag.com",
    "phys.org",
    "nature.com",
    "science.org",
    "cbsnews.com",
    "cnn.com",
    "spaceflightnow.com",
    "snopes.com",
    "factcheck.org",
    "politifact.com",
)


def public_url(url, *, media=False):
    p = urlsplit(url)
    scheme = p.scheme.lower()
    if (
        scheme not in ("https", "http")
        or not p.hostname
        or p.username
        or p.password
        or p.port not in (None, 80, 443)
    ):
        raise ValueError(
            "Only public HTTP/HTTPS URLs without credentials are supported"
        )
    host = p.hostname.lower().rstrip(".")
    if media:
        if host not in MEDIA_HOSTS or not p.path.lower().endswith(
            (".mp4", ".webm", ".mov")
        ):
            raise ValueError(
                "Supported URLs are direct MP4/WebM/MOV files on NASA media servers or Wikimedia Commons. Upload other accessible videos instead."
            )
    elif not any(host == d or host.endswith("." + d) for d in DOCUMENT_DOMAINS):
        raise ValueError(
            "This source is linked but automatic inspection is outside the current public-domain coverage"
        )
    port = p.port or (443 if scheme == "https" else 80)
    addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not addresses or any(
        not ipaddress.ip_address(a[4][0]).is_global for a in addresses
    ):
        raise ValueError("Private or non-public destinations are not supported")
    target_scheme = "https" if scheme == "https" or port == 443 else "http"
    return urlunsplit((target_scheme, p.netloc, p.path, p.query, ""))


class PageText(HTMLParser):
    BLOCKED: ClassVar[set[str]] = {
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "noscript",
        "svg",
        "template",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCKED:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in self.BLOCKED:
            self.depth = max(0, self.depth - 1)

    def handle_data(self, data):
        if not self.depth:
            self.parts.append(data)


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


async def download_video(url, target):
    current = public_url(url, media=True)
    async with httpx.AsyncClient(timeout=60, follow_redirects=False) as client:
        for _ in range(4):
            async with client.stream(
                "GET", current, headers={"User-Agent": "CONTEXT-Research/0.3"}
            ) as response:
                if response.is_redirect:
                    current = public_url(str(response.next_request.url), media=True)
                    continue
                response.raise_for_status()
                size = 0
                with target.open("wb") as out:
                    async for block in response.aiter_bytes():
                        size += len(block)
                        if size > 200 * 1024 * 1024:
                            raise ValueError("URL video exceeds 200 MB")
                        out.write(block)
                return {
                    "submitted_url": url,
                    "resolved_url": current,
                    "bytes": size,
                    "identity_status": "URL provenance only; footage identity is not independently verified",
                }
    raise ValueError("Too many media redirects")


def search_receipts(payload):
    calls = [x for x in payload.get("output", []) if x.get("type") == "web_search_call"]
    # A model-written link without a provider search receipt is not discovery.
    if not calls:
        return [], False
    sources = {}
    for call in calls:
        for item in call.get("results", []):
            if item.get("url"):
                sources[item["url"]] = {
                    "url": item["url"],
                    "title": item.get("title", item["url"]),
                    "search_snippet": item.get("snippet", ""),
                    "discovery": "provider_search_result",
                }
    for item in payload.get("output", []):
        for block in item.get("content", []):
            for citation in block.get("annotations", []):
                if citation.get("type") == "url_citation" and citation.get("url"):
                    sources.setdefault(
                        citation["url"],
                        {
                            "url": citation["url"],
                            "title": citation.get("title", citation["url"]),
                            "search_snippet": "",
                            "discovery": "provider_search_citation",
                        },
                    )
                    sources[citation["url"]]["cited_by_provider"] = True
    return list(sources.values()), True


def select_sources(candidates, queries, limit=8):
    """Rank actual search receipts before the bounded inspection budget.

    Receipt order reflects query order, not evidence quality. Prioritize cited,
    inspectable primary documents; keep every candidate in the saved audit.
    Domain preference is a fetch strategy, never a truth judgment.
    """
    terms = set(re.findall(r"[a-z0-9]+", " ".join(queries).lower()))
    terms -= {"a", "an", "the", "was", "it", "of", "to", "on", "and", "is", "in", "or"}

    def score(source):
        try:
            parsed = urlsplit(source["url"])
            host = (parsed.hostname or "").lower().rstrip(".")
        except ValueError:
            return (-1, -1, -1, -1)
        inspectable = any(host == d or host.endswith("." + d) for d in DOCUMENT_DOMAINS)
        html = not parsed.path.lower().endswith(
            (".pdf", ".mp4", ".jpg", ".png", ".zip")
        )
        primary = host.endswith((".gov", ".gov.uk", ".int", ".edu"))
        words = set(
            re.findall(
                r"[a-z0-9]+",
                (
                    source.get("title", "")
                    + " "
                    + parsed.path
                    + " "
                    + source.get("search_snippet", "")
                ).lower(),
            )
        )
        return (
            int(inspectable and html),
            int(source.get("cited_by_provider", False)),
            int(primary),
            len(terms & words),
        )

    ranked = sorted(candidates, key=score, reverse=True)
    return [
        {**source, "selection_score": list(score(source))} for source in ranked[:limit]
    ]


async def inspect_source(source):
    result = {
        **source,
        "fetch_status": "unavailable",
        "text": "",
        "quote_policy": "Exact excerpts; timestamp bounds do not establish truth.",
    }
    try:
        current = public_url(source["url"])
        async with httpx.AsyncClient(timeout=25, follow_redirects=False) as client:
            for _ in range(4):
                async with client.stream(
                    "GET", current, headers={"User-Agent": "CONTEXT-Research/0.3"}
                ) as response:
                    if response.is_redirect:
                        current = public_url(str(response.next_request.url))
                        continue
                    result["http_status"] = response.status_code
                    response.raise_for_status()
                    if not any(
                        t in response.headers.get("content-type", "")
                        for t in ("text/html", "text/plain")
                    ):
                        raise ValueError(
                            "Source is not an inspectable HTML/text document"
                        )
                    data = b""
                    async for chunk in response.aiter_bytes():
                        data += chunk
                        if len(data) > 2 * 1024 * 1024:
                            raise ValueError("Source exceeds inspection size limit")
                    parser = PageText()
                    parser.feed(data.decode("utf-8", errors="replace"))
                    text = normalize(" ".join(parser.parts))
                    if len(text) < 100:
                        raise ValueError("Insufficient accessible document text")
                    result.update(
                        fetch_status="fetched",
                        resolved_url=current,
                        text=text[:18000],
                        content_sha256=hashlib.sha256(data).hexdigest(),
                    )
                    return result
        raise ValueError("Too many source redirects")
    except (httpx.HTTPError, ValueError, OSError) as exc:
        result["fetch_error"] = str(exc)[:300]
    return result
