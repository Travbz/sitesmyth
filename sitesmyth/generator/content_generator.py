"""Generate website copy and image selection using Gemini Flash."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import google.generativeai as genai

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)


def _load_template_names() -> list[str]:
    """Return available template base names (without .html)."""
    tpl_dir = Path(__file__).parent / "templates"
    return [p.stem for p in tpl_dir.glob("*.html")]


def _select_template(category: str | None) -> str:
    """Select template based on business category."""
    cat = (category or "").lower()
    if any(kw in cat for kw in ["restaurant", "cafe", "food", "bar", "pub"]):
        return "restaurant"
    if any(kw in cat for kw in ["plumb", "hvac", "electric", "landscap", "contractor", "repair"]):
        return "home-services"
    return "generic"


def generate_content(lead_id: int, data_dir: Path, output_dir: Path) -> dict:
    """Generate website copy and image selection for a lead. Returns content dict."""
    cfg = Config.load()
    if not cfg.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY required for content generation.")

    genai.configure(api_key=cfg.gemini_api_key)
    model = genai.GenerativeModel(cfg.gemini_model)

    session = get_session(cfg.database_url)
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        raise ValueError(f"Lead {lead_id} not found")

    contents = session.query(ScrapedContent).filter(ScrapedContent.lead_id == lead_id).all()
    captions = [c.content_text for c in contents if c.content_text and c.content_type == "post_caption"]
    image_paths = [c.image_path for c in contents if c.image_path]
    session.close()

    text_context = "\n".join(captions[:15])[:4000] if captions else f"{lead.business_name} is a {lead.category or 'local business'} in {lead.city or 'the area'}."

    prompt = f"""Generate website copy for {lead.business_name}, a {lead.category or 'local business'} in {lead.city or 'the area'}.

Use this social media content as the source of truth:
{text_context}

Return a JSON object with exactly these keys:
- tagline: string, max 10 words, catchy
- about: string, 2-3 sentences professional description
- services: array of {{"title": string, "description": string}}, 4-6 items
- call_to_action: string, e.g. "Call us today" or "Book your appointment"

Output ONLY valid JSON, no markdown or extra text."""

    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    data = json.loads(text)

    hero_image = "images/hero.jpg"
    gallery_images = []
    lead_img_dir = data_dir / str(lead_id) / "images"
    if lead_img_dir.exists():
        imgs = sorted(lead_img_dir.glob("*.webp")) or sorted(lead_img_dir.glob("*.jpg"))
        if imgs:
            hero_image = f"images/{imgs[0].name}"
            gallery_images = [f"images/{p.name}" for p in imgs[:6]]

    return {
        "tagline": data.get("tagline", lead.business_name),
        "about": data.get("about", f"{lead.business_name} serves {lead.city or 'the community'}."),
        "services": data.get("services", [{"title": "Service", "description": "Quality service you can trust."}]),
        "call_to_action": data.get("call_to_action", "Contact us today"),
        "hero_image": hero_image,
        "gallery_images": gallery_images or [hero_image],
        "template": _select_template(lead.category),
    }
