"""Find Facebook and Instagram profiles for leads missing social links."""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

import requests
from thefuzz import fuzz

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead

log = logging.getLogger(__name__)


def _google_search(query: str, limit: int = 5) -> list[str]:
    """Simple Google search via requests — returns URLs. For production, use SerpAPI or similar."""
    try:
        # Use a simple HTTP request; for real use, integrate SerpAPI, Bing API, or Apify Google Search
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SiteSmyth/1.0)"}
        resp = requests.get(
            f"https://www.google.com/search?q={requests.utils.quote(query)}",
            headers=headers,
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        # Naive extraction of links from HTML (Google blocks direct scraping; this is a fallback)
        # In production: use Apify Google Search actor or SerpAPI
        urls = re.findall(r'href="(https?://[^"]+)"', resp.text)
        return [u for u in urls if "google." not in u and "youtube." not in u][:limit]
    except Exception as e:
        log.debug("Google search failed: %s", e)
        return []


def _extract_facebook_url(urls: list[str], business_name: str, city: str) -> str | None:
    """Extract likely Facebook page URL from search results."""
    for u in urls:
        if "facebook.com" in u and "/pages/" not in u:
            path = urlparse(u).path.strip("/")
            if path and path != "sharer" and path != "share":
                return u
    return None


def _extract_instagram_handle(urls: list[str], business_name: str) -> str | None:
    """Extract Instagram handle from URLs; optionally fuzzy-match to business name."""
    for u in urls:
        if "instagram.com/" in u:
            path = urlparse(u).path.strip("/").split("/")[0]
            if path and path not in ("p", "reel", "stories", "explore"):
                if fuzz.ratio(path.lower(), business_name.lower().replace(" ", "")) > 50:
                    return path
                return path  # Return anyway; user can verify
    return None


def find_social_profiles(lead_id: int | None = None, limit: int | None = None) -> int:
    """For leads missing facebook_url or instagram_handle, attempt to find them.

    Uses Google search fallback. For production, consider Apify actors for FB/IG search.
    Returns number of leads updated with new social data.
    """
    cfg = Config.load()
    session = get_session(cfg.database_url)

    query = session.query(Lead).filter(Lead.status == "discovered")
    if lead_id:
        query = query.filter(Lead.id == lead_id)
    if limit:
        query = query.limit(limit)

    leads = query.all()
    updated = 0

    for lead in leads:
        needs_facebook = not lead.facebook_url
        needs_instagram = not lead.instagram_handle
        if not needs_facebook and not needs_instagram:
            continue

        city = lead.city or lead.zip_code or ""
        search_query = f'"{lead.business_name}" {city}'
        if needs_facebook:
            search_query_fb = f'"{lead.business_name}" {city} facebook'
            urls = _google_search(search_query_fb, limit=5)
            fb = _extract_facebook_url(urls, lead.business_name, city)
            if fb:
                lead.facebook_url = fb
                updated += 1

        if needs_instagram:
            search_query_ig = f'"{lead.business_name}" {city} instagram'
            urls = _google_search(search_query_ig, limit=5)
            ig = _extract_instagram_handle(urls, lead.business_name)
            if ig:
                lead.instagram_handle = ig
                updated += 1

    session.commit()
    session.close()
    return updated
