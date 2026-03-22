"""Filter leads based on social media activity recency.

Checks scraped post timestamps or post count to determine if a business
is actively posting. Leads with no recent activity get marked as 'stale'.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)

STALE_MONTHS = 6
MIN_POSTS_FOR_ACTIVE = 3


def filter_inactive_leads(lead_id: int | None = None, limit: int = 50) -> dict:
    """Check scraped leads for social media activity. Returns stats dict.

    A lead is marked 'stale' if:
    - It has fewer than MIN_POSTS_FOR_ACTIVE captions, OR
    - All its scraped_at timestamps are older than STALE_MONTHS months

    A lead that passes stays 'scraped' and proceeds to content scoring.
    """
    cfg = Config.load()
    session = get_session(cfg.database_url)

    query = session.query(Lead).filter(Lead.status == "scraped")
    if lead_id:
        query = query.filter(Lead.id == lead_id)
    leads = query.limit(limit).all()

    stats = {"checked": 0, "active": 0, "stale": 0}
    cutoff = datetime.utcnow() - timedelta(days=STALE_MONTHS * 30)

    for lead in leads:
        stats["checked"] += 1
        contents = session.query(ScrapedContent).filter(
            ScrapedContent.lead_id == lead.id
        ).all()

        captions = [c for c in contents if c.content_type == "post_caption" and c.content_text]
        has_enough_posts = len(captions) >= MIN_POSTS_FOR_ACTIVE

        has_any_content = len(captions) > 0 or any(
            c.content_type == "bio" and c.content_text for c in contents
        )

        # Check scraped_at timestamps if available
        recent_content = False
        for c in contents:
            if c.scraped_at and c.scraped_at > cutoff:
                recent_content = True
                break

        # If no scraped_at timestamps, assume content is recent (freshly scraped)
        if not any(c.scraped_at for c in contents):
            recent_content = True

        is_active = has_enough_posts and has_any_content and recent_content

        if is_active:
            stats["active"] += 1
            log.info("  ✓ %s: active (%d posts)", lead.business_name, len(captions))
        else:
            reasons = []
            if not has_enough_posts:
                reasons.append(f"only {len(captions)} posts (need {MIN_POSTS_FOR_ACTIVE})")
            if not has_any_content:
                reasons.append("no content at all")
            if not recent_content:
                reasons.append(f"no posts since {cutoff.strftime('%Y-%m')}")
            lead.status = "stale"
            stats["stale"] += 1
            log.info("  ✗ %s: stale (%s)", lead.business_name, ", ".join(reasons))

    session.commit()
    session.close()
    return stats
