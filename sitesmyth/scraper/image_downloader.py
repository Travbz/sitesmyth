"""Resize and optimize scraped images for web. Optional: categorize with Gemini vision."""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import ScrapedContent

log = logging.getLogger(__name__)

MAX_WIDTH = 1200
QUALITY = 85


def optimize_images(lead_id: int, data_dir: Path) -> int:
    """Resize images to max 1200px wide, save as WebP. Returns count processed."""
    cfg = Config.load()
    session = get_session(cfg.database_url)
    contents = session.query(ScrapedContent).filter(
        ScrapedContent.lead_id == lead_id,
        ScrapedContent.image_path.isnot(None),
    ).all()

    processed = 0
    for sc in contents:
        if not sc.image_path:
            continue
        src = data_dir / sc.image_path
        if not src.exists():
            continue
        try:
            out_path = src.with_suffix(".webp")
            img = Image.open(src).convert("RGB")
            w, h = img.size
            if w > MAX_WIDTH:
                ratio = MAX_WIDTH / w
                new_h = int(h * ratio)
                img = img.resize((MAX_WIDTH, new_h), Image.Resampling.LANCZOS)
            img.save(out_path, "WEBP", quality=QUALITY)
            if out_path != src:
                src.unlink(missing_ok=True)
            sc.image_path = str(out_path.relative_to(data_dir))
            processed += 1
        except Exception as e:
            log.debug("Optimize failed %s: %s", src, e)

    session.commit()
    session.close()
    return processed
