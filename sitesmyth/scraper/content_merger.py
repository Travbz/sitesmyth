"""Merge Facebook + Instagram content for leads with both platforms."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)


def _image_hash(path: Path) -> str | None:
    """Simple hash of file content for deduplication."""
    if not path.exists():
        return None
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except OSError:
        return None


def merge_content(lead_id: int, data_dir: Path) -> None:
    """For leads with both FB and IG, merge and deduplicate. Updates scraped_content.

    Merge rules per plan:
    - Business description: prefer FB About (we store post captions; no separate About in scraped_content)
    - Gallery: combine images, dedupe by hash
    - Contact: FB preferred (in Lead model, not scraped_content)
    """
    cfg = Config.load()
    session = get_session(cfg.database_url)
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        return

    contents = session.query(ScrapedContent).filter(ScrapedContent.lead_id == lead_id).all()
    fb_images = [c for c in contents if c.source == "facebook" and c.image_path]
    ig_images = [c for c in contents if c.source == "instagram" and c.image_path]

    seen_hashes: set[str] = set()
    for sc in fb_images + ig_images:
        if not sc.image_path:
            continue
        full_path = data_dir / sc.image_path
        h = _image_hash(full_path)
        if h and h in seen_hashes:
            session.delete(sc)
        elif h:
            seen_hashes.add(h)

    session.commit()
    session.close()
