"""Score scraped content to decide if a lead has enough material for site generation."""

from __future__ import annotations

import logging

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)

THRESHOLD = 15


def score_lead(lead_id: int) -> int:
    """Compute content score for a lead based on scraped data. Updates DB and returns score."""
    cfg = Config.load()
    session = get_session(cfg.database_url)

    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        return 0

    contents = session.query(ScrapedContent).filter(ScrapedContent.lead_id == lead_id).all()

    num_captions = sum(1 for c in contents if c.content_type == "post_caption" and c.content_text)
    num_images = sum(1 for c in contents if c.content_type == "image" and c.image_path)
    has_bio = any(c.content_type == "bio" and c.content_text for c in contents)
    has_address = bool(lead.address)
    has_phone = bool(lead.phone)

    score = (
        num_captions * 2
        + num_images * 1
        + (10 if has_bio else 0)
        + (5 if has_address else 0)
        + (5 if has_phone else 0)
    )

    lead.content_score = score
    if score < THRESHOLD:
        lead.status = "low_content"
        log.info("  %s: content_score=%d (below threshold %d) → low_content", lead.business_name, score, THRESHOLD)
    else:
        log.info("  %s: content_score=%d (passes threshold %d)", lead.business_name, score, THRESHOLD)

    session.commit()
    session.close()
    return score


def score_all_scraped() -> int:
    """Score all leads in 'scraped' status. Returns count scored."""
    cfg = Config.load()
    session = get_session(cfg.database_url)
    leads = session.query(Lead).filter(Lead.status == "scraped").all()
    session.close()

    scored = 0
    for lead in leads:
        score_lead(lead.id)
        scored += 1
    return scored
