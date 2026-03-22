"""Ghostwrite a site-building prompt from scraped social content via Gemini."""

from __future__ import annotations

import logging
from datetime import date

import google.generativeai as genai

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are ghostwriting a description of a small business that will be used to \
generate a professional website design. Write as the owner — first person, \
conversational. "I run X, we do Y, our vibe is..."

Today's date is {today}.

Include: who they are, what they do, their real services (from the social posts \
provided), their address/phone, and what kind of vibe/personality their brand has.

CRITICAL RULES:
- ONLY describe what is explicitly stated in the social posts. If a post mentions \
  bands playing, that's content to feature — but do NOT extrapolate the entire \
  business identity from one or two posts. Describe what you SEE, not what you infer.
- NEVER invent specific dates, times, prices, or event schedules. If posts mention \
  events without dates, say "check back for upcoming events" — do NOT make up dates.
- NEVER invent services, menu items, or features not explicitly described in the content.
- If the Google Maps category says "restaurant" but posts are about live music, \
  treat it as BOTH — "we're a restaurant with live entertainment" not purely a music venue.
- If social posts are sparse (fewer than 5), keep descriptions general and factual. \
  Do NOT pad with invented details.
- Describe the BRAND VIBE: is it rustic? modern? luxury? family-friendly? edgy? \
  This helps the designer choose the right colors and typography.

Aim for 200-400 words. Output ONLY the ghostwritten description. No preamble."""


def plan_site(lead_id: int) -> str:
    """Generate a ghostwritten site-building prompt for a lead. Saves to DB."""
    cfg = Config.load()
    if not cfg.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY required for planning.")

    genai.configure(api_key=cfg.gemini_api_key)
    model = genai.GenerativeModel(cfg.gemini_model)

    session = get_session(cfg.database_url)
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        raise ValueError(f"Lead {lead_id} not found")

    contents = session.query(ScrapedContent).filter(ScrapedContent.lead_id == lead_id).all()

    context = _build_context(lead, contents)

    user_prompt = (
        "Based on the context below, write the natural description that this business owner "
        "would use to describe their business for a website. Output only the description — "
        "no preamble, no sections, no meta-commentary.\n\n"
        + context
    )

    system = SYSTEM_PROMPT.format(today=date.today().strftime("%B %d, %Y"))
    response = model.generate_content(
        [{"role": "user", "parts": [system + "\n\n" + user_prompt]}]
    )
    brief = response.text.strip()

    lead.site_brief = brief
    session.commit()
    session.close()

    log.info("  Planned %s (%d chars)", lead.business_name, len(brief))
    return brief


def _build_context(lead: Lead, contents: list[ScrapedContent]) -> str:
    parts = [
        "## Business Info",
        f"- **Name**: {lead.business_name}",
        f"- **Category**: {lead.category or 'Local Business'}",
        f"- **Address**: {lead.address or 'Not available'}",
        f"- **City**: {lead.city or 'Unknown'}, {lead.state or ''}",
        f"- **Phone**: {lead.phone or 'Not available'}",
    ]

    if lead.facebook_url:
        parts.append(f"- **Facebook**: {lead.facebook_url}")
    if lead.instagram_handle:
        parts.append(f"- **Instagram**: @{lead.instagram_handle}")

    captions = [c.content_text for c in contents if c.content_text and c.content_type == "post_caption"]
    bios = [c.content_text for c in contents if c.content_text and c.content_type == "bio"]

    if bios:
        parts.append("\n## Social Media Bio")
        for bio in bios[:2]:
            parts.append(bio[:500])

    if captions:
        parts.append(f"\n## Social Media Posts ({len(captions)} posts scraped)")
        parts.append("Use these to understand what the business does and how they talk about themselves.\n")
        for i, cap in enumerate(captions[:12]):
            parts.append(f"**Post {i+1}**: {cap[:400]}")

    return "\n".join(parts)
