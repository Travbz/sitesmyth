"""Merge Facebook + Instagram content for leads with both platforms."""

from __future__ import annotations

import logging

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)


def merge_content(lead_id: int) -> None:
    """For leads with both FB and IG, deduplicate near-identical text posts."""
    cfg = Config.load()
    session = get_session(cfg.database_url)
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        return

    contents = session.query(ScrapedContent).filter(
        ScrapedContent.lead_id == lead_id,
        ScrapedContent.content_type == "post_caption",
    ).all()

    seen_texts: set[str] = set()
    removed = 0
    for sc in contents:
        if not sc.content_text:
            continue
        normalized = sc.content_text.strip().lower()[:200]
        if normalized in seen_texts:
            session.delete(sc)
            removed += 1
        else:
            seen_texts.add(normalized)

    if removed:
        log.info("  Deduped %d duplicate text posts for lead %d", removed, lead_id)

    session.commit()
    session.close()
