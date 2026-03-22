"""Build static HTML site from template and generated content."""

from __future__ import annotations

import json
import re
from pathlib import Path

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead

GENERIC_KEYWORDS = ["retail", "shop", "store", "boutique", "professional", "legal", "accounting"]


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower().strip()).strip("-")[:80]


def _build_google_maps_embed(address: str, maps_url: str | None) -> str:
    """Return link or embed for Google Maps."""
    if maps_url and "google.com/maps" in maps_url:
        return f'<a href="{maps_url}" target="_blank" rel="noopener" class="text-blue-600 underline">View on Google Maps</a>'
    return ""


def build_site(lead_id: int, content: dict, data_dir: Path, output_dir: Path, cfg: Config) -> Path:
    """Build static site to output_dir/{slug}. Returns path to site folder."""
    session = get_session(cfg.database_url)
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        raise ValueError(f"Lead {lead_id} not found")

    slug = _slugify(lead.business_name)
    site_dir = output_dir / slug
    site_dir.mkdir(parents=True, exist_ok=True)
    img_dir = site_dir / "images"
    img_dir.mkdir(exist_ok=True)

    # Copy images from data to site
    for img_rel in content.get("gallery_images", []) + [content.get("hero_image", "")]:
        if not img_rel:
            continue
        src = data_dir / str(lead_id) / "images" / Path(img_rel).name
        if not src.exists():
            src = data_dir / str(lead_id) / img_rel
        if src.exists():
            (img_dir / src.name).write_bytes(src.read_bytes())

    hero_rel = content.get("hero_image", "images/hero.jpg")
    if not (site_dir / hero_rel).exists() and img_dir.exists():
        first_img = next(img_dir.iterdir(), None)
        hero_rel = f"images/{first_img.name}" if first_img else "images/placeholder.jpg"

    services_html = ""
    for svc in content.get("services", []):
        title = svc.get("title", "Service")
        desc = svc.get("description", "")
        services_html += f'<div class="p-4 border rounded"><h4 class="font-semibold">{title}</h4><p class="text-sm text-gray-500">{desc}</p></div>'

    gallery_html = ""
    for img in content.get("gallery_images", [])[:6]:
        gallery_html += f'<img src="{img}" alt="Photo" class="w-full h-48 object-cover rounded">'

    instagram_link = ""
    if lead.instagram_handle:
        instagram_link = f'<a href="https://instagram.com/{lead.instagram_handle}" class="block text-blue-600 mt-2" target="_blank">Instagram</a>'

    maps_embed = _build_google_maps_embed(lead.address or "", lead.google_maps_url)

    tpl_name = content.get("template", "generic")
    tpl_path = Path(__file__).parent / "templates" / f"{tpl_name}.html"
    if not tpl_path.exists():
        tpl_path = Path(__file__).parent / "templates" / "generic.html"

    html = tpl_path.read_text()
    html = html.replace("{{business_name}}", lead.business_name or "")
    html = html.replace("{{tagline}}", content.get("tagline", ""))
    html = html.replace("{{about}}", content.get("about", ""))
    html = html.replace("{{services}}", services_html)
    html = html.replace("{{gallery_images}}", gallery_html)
    html = html.replace("{{hero_image}}", hero_rel)
    html = html.replace("{{phone}}", lead.phone or "")
    html = html.replace("{{address}}", lead.address or "")
    html = html.replace("{{instagram_link}}", instagram_link)
    html = html.replace("{{google_maps_embed}}", maps_embed)
    html = html.replace("{{call_to_action}}", content.get("call_to_action", "Contact us"))
    html = html.replace("{{contact_phone}}", cfg.contact_phone or "(555) 123-4567")

    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": lead.business_name,
        "address": lead.address,
        "telephone": lead.phone,
    }
    schema_script = f'<script type="application/ld+json">{json.dumps(schema)}</script>'
    html = html.replace("</head>", f"{schema_script}\n</head>")

    (site_dir / "index.html").write_text(html, encoding="utf-8")
    session.close()
    return site_dir
