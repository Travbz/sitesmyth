"""Scrape Facebook page content for site generation."""

from __future__ import annotations

import logging
from pathlib import Path

import requests
from apify_client import ApifyClient

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)

FB_POSTS_ACTOR = "apify/facebook-posts-scraper"


def _download_image(url: str, dest: Path) -> bool:
    """Download image to dest. Returns True on success."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "SiteSmyth/1.0"})
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        return True
    except Exception as e:
        log.debug("Download failed %s: %s", url, e)
        return False


def scrape_facebook(lead_id: int, data_dir: Path) -> int:
    """Scrape Facebook content for a lead. Returns count of scraped content items."""
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
    run = actor.call(
        run_input={
            "startUrls": [{"url": lead.facebook_url}],
            "maxPosts": 15,
        },
        timeout=120,
    )
    if not run:
        session.close()
        return 0

    dataset = client.dataset(run.default_dataset_id)
    items = list(dataset.iterate_items())

    lead_dir = data_dir / str(lead_id) / "images"
    lead_dir.mkdir(parents=True, exist_ok=True)
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

        images = item.get("images") or item.get("imageUrls") or []
        if isinstance(images, str):
            images = [images]
        for i, img_url in enumerate(images[:5]):
            if not img_url:
                continue
            fname = f"fb_post_{hash(img_url) % 10**8}.jpg"
            dest = lead_dir / fname
            if _download_image(img_url, dest):
                sc = ScrapedContent(
                    lead_id=lead_id,
                    source="facebook",
                    content_type="image",
                    image_path=str(dest.relative_to(data_dir)),
                    image_category="general",
                )
                session.add(sc)
                count += 1

    lead.status = "scraped"
    session.commit()
    session.close()
    return count
