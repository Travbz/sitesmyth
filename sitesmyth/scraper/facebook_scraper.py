"""Scrape Facebook page content for site generation."""

from __future__ import annotations

import logging

from apify_client import ApifyClient

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)

FB_POSTS_ACTOR = "apify/facebook-posts-scraper"


def scrape_facebook(lead_id: int) -> int:
    """Scrape Facebook text content for a lead. Returns count of scraped items.

    Images are NOT downloaded — Stitch generates CSS-only designs and doesn't
    need them. Only post text is stored in the DB.
    """
    cfg = Config.load()
    if not cfg.apify_api_token:
        raise RuntimeError("APIFY_API_TOKEN required.")

    session = get_session(cfg.database_url)
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead or not lead.facebook_url:
        session.close()
        return 0

    client = ApifyClient(cfg.apify_api_token)
    actor = client.actor(FB_POSTS_ACTOR)
    run = actor.call(run_input={
        "startUrls": [{"url": lead.facebook_url}],
        "maxPosts": 15,
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
        text = item.get("text") or item.get("message") or item.get("content")
        if text:
            sc = ScrapedContent(
                lead_id=lead_id,
                source="facebook",
                content_type="post_caption",
                content_text=text[:5000],
            )
            session.add(sc)
            count += 1

    lead.status = "scraped"
    session.commit()
    session.close()
    return count
