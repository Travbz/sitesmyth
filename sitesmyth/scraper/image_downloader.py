"""Image optimization — no-op with Stitch builder (CSS-only designs, no images needed)."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def optimize_images(lead_id: int) -> int:
    """No-op: Stitch generates CSS-only designs; images aren't downloaded or embedded."""
    return 0
