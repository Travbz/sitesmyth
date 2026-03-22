"""Scrape Instagram profile content for site generation."""

from __future__ import annotations

import logging

from apify_client import ApifyClient

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)

IG_ACTOR = "apify/instagram-post-scraper"


def scrape_instagram(lead_id: int) -> int:
    """Scrape Instagram text content for a lead. Returns count of scraped items.

    Images are NOT downloaded — Stitch generates CSS-only designs and doesn't
    need them. Only captions/bios are stored in the DB.
    """
    cfg = Config.load()
    if not cfg.apify_api_token:
        raise RuntimeError("APIFY_API_TOKEN required.")

    session = get_session(cfg.database_url)
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead or not lead.instagram_handle:
        session.close()
        return 0

    client = ApifyClient(cfg.apify_api_token)
    actor = client.actor(IG_ACTOR)
    run = actor.call(run_input={
        "username": [lead.instagram_handle],
        "resultsLimit": 20,
    })
    if not run:
        session.close()
        return 0

    dataset_id = run.get("defaultDatasetId") if isinstance(run, dict) else getattr(run, "default_dataset_id", None)
    if not dataset_id:
        session.close()
        return 0
    dataset = client.dataset(dataset_id)
    items = list(dataset.iterate_items())

    count = 0
    for item in items:
        caption = item.get("caption") or item.get("text")
        if caption:
            sc = ScrapedContent(
                lead_id=lead_id,
                source="instagram",
                content_type="post_caption",
                content_text=(caption or "")[:5000],
            )
            session.add(sc)
            count += 1

    lead.status = "scraped"
    session.commit()
    session.close()
    return count
