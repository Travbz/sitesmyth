"""Generate Instagram DM queue for manual sending."""

from __future__ import annotations

import csv
from pathlib import Path

from sitesmyth.config import Config
from sitesmyth.db.queries import get_sendable_leads


DM_TEMPLATE = """Hey! I came across {business_name} and noticed you don't have a website yet. Your content is great though — I put together a quick demo site for you:
{site_url}
Let me know what you think!"""


def generate_dm_queue(limit: int = 15) -> Path:
    """Generate CSV of DMs to send manually (for leads with no email). Returns path to CSV."""
    from sitesmyth.db import get_session

    cfg = Config.load()
    session = get_session(cfg.database_url)

    leads = get_sendable_leads(session, "instagram_dm", sequence_number=1, limit=limit)
    leads = [l for l in leads if not l.email or not l.email.strip()]
    session.close()

    out_path = Path("dm_queue.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["business_name", "ig_handle", "dm_text", "site_url"])
        for lead in leads:
            if not lead.instagram_handle or not lead.site_url:
                continue
            text = DM_TEMPLATE.format(
                business_name=lead.business_name or "",
                site_url=lead.site_url or "",
            )
            w.writerow([lead.business_name, lead.instagram_handle, text, lead.site_url])

    return out_path
