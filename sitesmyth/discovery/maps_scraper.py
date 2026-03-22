"""Google Maps discovery — uses Places API if GOOGLE_MAPS_KEY set, else Apify."""

from __future__ import annotations

import json
import logging
import re
import time

import httpx
from apify_client import ApifyClient

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead

log = logging.getLogger(__name__)

PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
MAPS_ACTOR_ID = "compass/crawler-google-places"


def slugify(name: str) -> str:
    """Sanitize business name to URL-safe slug."""
    s = re.sub(r"[^a-z0-9]+", "-", name.lower().strip()).strip("-")
    return s[:80] if s else "unknown"


def _discover_via_places_api(
    cfg: Config,
    zip_code: str | None,
    city: str | None,
    state: str,
    categories: list[str],
    max_per_search: int,
) -> int:
    """Discover via Google Places API (New). Filters to no-website only."""
    location_str = zip_code if zip_code else f"{city or ''} {state}".strip() or "USA"
    session = get_session(cfg.database_url)
    new_count = 0

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": cfg.google_maps_key,
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.formattedAddress,"
            "places.nationalPhoneNumber,places.internationalPhoneNumber,"
            "places.websiteUri,places.primaryTypeDisplayName,places.rating,"
            "places.userRatingCount,places.googleMapsUri,"
            "nextPageToken"
        ),
    }

    for category in categories:
        text_query = f"{category} in {location_str}"
        page_token: str | None = None
        fetched = 0

        while fetched < max_per_search:
            body: dict = {"textQuery": text_query, "pageSize": 20}
            if page_token:
                body["pageToken"] = page_token

            resp = httpx.post(PLACES_TEXT_SEARCH_URL, json=body, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            for place in data.get("places", []):
                website = place.get("websiteUri") or ""
                if website and website.strip():
                    continue
                display_name = place.get("displayName", {})
                name = display_name.get("text", "") if isinstance(display_name, dict) else str(display_name)
                if not name.strip():
                    continue

                slug = slugify(name)
                if session.query(Lead).filter(Lead.slug == slug).first():
                    continue

                primary_type = place.get("primaryTypeDisplayName", {})
                category_val = primary_type.get("text", "") if isinstance(primary_type, dict) else str(primary_type)

                lead = Lead(
                    business_name=name.strip(),
                    slug=slug,
                    category=category_val,
                    address=place.get("formattedAddress", ""),
                    city=city or None,
                    state=state if state != "USA" else None,
                    zip_code=zip_code,
                    phone=place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber"),
                    email=None,
                    google_maps_url=place.get("googleMapsUri"),
                    facebook_url=None,
                    instagram_handle=None,
                    has_website=False,
                    status="discovered",
                )
                session.add(lead)
                new_count += 1

            fetched += 20
            page_token = data.get("nextPageToken")
            if not page_token:
                break
            time.sleep(0.2)

    session.commit()
    session.close()
    return new_count


def run_maps_discovery(
    *,
    zip_code: str | None = None,
    city: str | None = None,
    state: str | None = None,
    categories: list[str] | None = None,
    max_per_search: int = 100,
) -> int:
    """Run Apify Google Maps scraper, filter to no-website businesses, store in DB.

    Args:
        zip_code: e.g. "45202"
        city: e.g. "Cincinnati" (used with state if no zip)
        state: e.g. "OH"
        categories: e.g. ["restaurants", "plumbers"]
        max_per_search: max places per search term

    Returns:
        Number of new leads added.
    """
    cfg = Config.load()

    if cfg.google_maps_key:
        categories = categories or ["restaurant", "plumber", "landscaping"]
        log.info("Using Google Places API for discovery: location=%s, categories=%s", zip_code or f"{city or ''} {state or ''}".strip() or "USA", categories)
        return _discover_via_places_api(
            cfg, zip_code, city, state or "USA", categories, max_per_search
        )

    if not cfg.apify_api_token:
        raise RuntimeError("APIFY_API_TOKEN or GOOGLE_MAPS_KEY required for discovery.")

    location_query = zip_code if zip_code else f"{city or 'USA'}, {state or 'USA'}"
    search_strings = categories or ["restaurant", "plumber", "landscaping"]

    client = ApifyClient(cfg.apify_api_token)
    actor_client = client.actor(MAPS_ACTOR_ID)

    run_input = {
        "searchStringsArray": search_strings,
        "locationQuery": location_query,
        "maxCrawledPlacesPerSearch": max_per_search,
        "language": "en",
        "includeWebResults": False,
    }

    log.info("Running Apify actor %s: location=%s, searches=%s", MAPS_ACTOR_ID, location_query, search_strings)
    run_result = actor_client.call(run_input=run_input)

    if run_result is None:
        raise RuntimeError("Apify actor run failed.")

    dataset_client = client.dataset(run_result.default_dataset_id)
    items = list(dataset_client.iterate_items())

    session = get_session(cfg.database_url)
    new_count = 0

    for item in items:
        website = item.get("website") or ""
        if website and website.strip():
            continue  # Skip businesses that have a website

        title = (item.get("title") or "").strip()
        if not title:
            continue

        slug = slugify(title)
        existing = session.query(Lead).filter(Lead.slug == slug).first()
        if existing:
            continue

        address = item.get("address") or ""
        city_val = item.get("city") or ""
        state_val = item.get("state") or state or ""
        postal_code = item.get("postalCode") or zip_code or ""

        # Extract social links if present (from enrichment add-on; may be empty for no-website biz)
        facebooks = item.get("facebooks") or []
        instagrams = item.get("instagrams") or []
        facebook_url = facebooks[0] if isinstance(facebooks, list) and facebooks else None
        instagram_url = instagrams[0] if isinstance(instagrams, list) and instagrams else None
        instagram_handle = None
        if instagram_url and "instagram.com/" in str(instagram_url):
            parts = str(instagram_url).rstrip("/").split("/")
            instagram_handle = parts[-1] if parts else None

        # Capture GBP photo URLs for Stitch design theming
        gbp_photos = item.get("imageUrls") or item.get("images") or []
        if isinstance(gbp_photos, list):
            gbp_photos = [u for u in gbp_photos if isinstance(u, str) and u.startswith("http")][:10]

        lead = Lead(
            business_name=title,
            slug=slug,
            category=item.get("categoryName") or item.get("categories", [None])[0] if item.get("categories") else None,
            address=address,
            city=city_val,
            state=state_val,
            zip_code=postal_code or zip_code,
            phone=item.get("phone") or item.get("phoneUnformatted"),
            email=None,
            google_maps_url=item.get("url") or item.get("searchPageUrl"),
            facebook_url=facebook_url,
            instagram_handle=instagram_handle,
            has_website=False,
            status="discovered",
            gbp_photo_urls=json.dumps(gbp_photos) if gbp_photos else None,
        )
        session.add(lead)
        new_count += 1

    session.commit()
    session.close()

    log.info("Added %d new leads (no-website) from %d total places", new_count, len(items))
    return new_count
