"""Orchestrate outreach — waterfall (email → IG DM → FB DM), rate limits, suppression checks."""

from __future__ import annotations

import logging
import time
from datetime import datetime

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead
from sitesmyth.db.queries import get_sendable_leads
from sitesmyth.outreach.email_sender import send_email
from sitesmyth.outreach.instagram_dm import generate_dm_queue

log = logging.getLogger(__name__)


def run_outreach(
    *,
    channel: str = "email",
    sequence_number: int = 1,
    limit: int | None = None,
    lead_id: int | None = None,
    max_per_hour: int | None = None,
    dry_run: bool = False,
) -> dict[str, int]:
    """Run outreach. Returns stats: sent, skipped, failed."""
    cfg = Config.load()
    session = get_session(cfg.database_url)

    if channel == "instagram_dm":
        out_path = generate_dm_queue(limit=limit or 15)
        session.close()
        return {"dm_queue_path": str(out_path), "queued": 0}

    leads = get_sendable_leads(session, channel, sequence_number, limit=limit or (1 if lead_id else 50))
    if lead_id:
        leads = [l for l in leads if l.id == lead_id]
    session.close()

    sent = 0
    skipped = 0
    failed = 0
    rate = max_per_hour or cfg.max_emails_per_hour
    delay = 3600 / rate if rate else 0

    for lead in leads:
        if channel == "email":
            if not lead.email:
                skipped += 1
                continue
            if dry_run:
                log.info("DRY RUN: would send to %s <%s> re: %s", lead.business_name, lead.email, (lead.site_url or "no site"))
                sent += 1
                continue
            if send_email(lead, sequence_number, cfg):
                sent += 1
                if delay:
                    time.sleep(delay)
            else:
                failed += 1

    return {"sent": sent, "skipped": skipped, "failed": failed}
