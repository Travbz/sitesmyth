"""Google Stitch-powered site builder — generates polished HTML from a design prompt."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from sitesmyth.config import Config
from sitesmyth.db import get_session
from sitesmyth.db.models import Lead, ScrapedContent

log = logging.getLogger(__name__)


def _get_access_token() -> str:
    """Get OAuth access token from gcloud application-default credentials."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    # Try common homebrew location
    try:
        result = subprocess.run(
            ["/opt/homebrew/share/google-cloud-sdk/bin/gcloud",
             "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, timeout=15,
            env={**__import__("os").environ, "CLOUDSDK_PYTHON": "python3"},
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    raise RuntimeError(
        "Could not get OAuth token. Run: gcloud auth application-default login"
    )


def build_stitch_site(lead_id: int, output_dir: Path | None = None) -> Path:
    """Build a site for a lead using Google Stitch. Returns the output directory."""
    cfg = Config.load()
    if output_dir is None:
        output_dir = cfg.output_dir

    session = get_session(cfg.database_url)
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        raise ValueError(f"Lead {lead_id} not found")

    contents = session.query(ScrapedContent).filter(
        ScrapedContent.lead_id == lead_id
    ).all()
    session.close()

    slug = lead.slug
    site_dir = output_dir / slug

    # Clean old build artifacts
    if site_dir.exists():
        import shutil
        for item in ["node_modules", "dist", ".astro", "src", "public",
                     "package.json", "package-lock.json", "astro.config.mjs",
                     "tailwind.config.mjs", "build-error.log"]:
            p = site_dir / item
            if p.is_dir():
                shutil.rmtree(p)
            elif p.is_file():
                p.unlink()

    site_dir.mkdir(parents=True, exist_ok=True)

    brief = lead.site_brief if lead.site_brief else _build_fallback_brief(lead, contents)

    stitch_prompt = _build_stitch_prompt(lead, brief, contents, cfg)
    log.info("  Stitch prompt: %d chars", len(stitch_prompt))

    access_token = _get_access_token()
    html = _generate_with_stitch(stitch_prompt, access_token)

    html = _inject_seo(html, lead, cfg)
    html = _swap_photos(html, lead)

    out_path = site_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")

    # Write robots.txt
    robots = (
        "User-agent: *\nAllow: /\n\n"
        "User-agent: GPTBot\nAllow: /\n\n"
        "User-agent: ClaudeBot\nAllow: /\n\n"
        "User-agent: PerplexityBot\nAllow: /\n"
    )
    (site_dir / "robots.txt").write_text(robots, encoding="utf-8")

    log.info("  Stitch site built → %s (%d chars)", out_path, len(html))
    return site_dir


def _build_fallback_brief(lead: Lead, contents: list[ScrapedContent]) -> str:
    """If planner didn't run, build a minimal brief from lead data."""
    parts = [f"I run {lead.business_name}"]
    if lead.category:
        parts.append(f", a {lead.category.lower()}")
    if lead.city and lead.state:
        parts.append(f" in {lead.city}, {lead.state}")
    parts.append(".")
    if lead.address:
        parts.append(f" We're at {lead.address}.")
    if lead.phone:
        parts.append(f" Call us at {lead.phone}.")

    captions = [c.content_text for c in contents
                if c.content_text and c.content_type == "post_caption"]
    if captions:
        parts.append(f" Here's what we post about: {'; '.join(c[:100] for c in captions[:5])}")

    return "".join(parts)


def _build_stitch_prompt(
    lead: Lead, brief: str, contents: list[ScrapedContent], cfg: Config
) -> str:
    """Build the prompt we send to Stitch for design generation."""
    captions = [c.content_text for c in contents
                if c.content_text and c.content_type == "post_caption"]
    bios = [c.content_text for c in contents
            if c.content_text and c.content_type == "bio"]

    sections = [
        f"Design a modern, professional single-page website for {lead.business_name}.",
        "",
        f"Business type: {lead.category or 'Local Business'}",
        f"Location: {lead.address or lead.city or 'Unknown'}",
    ]

    if lead.phone:
        sections.append(f"Phone: {lead.phone}")
    if lead.facebook_url:
        sections.append(f"Facebook: {lead.facebook_url}")
    if lead.instagram_handle:
        sections.append(f"Instagram: @{lead.instagram_handle}")

    sections.append("")
    sections.append("Business description (from their own words):")
    sections.append(brief[:800])

    if bios:
        sections.append("")
        sections.append("Their social media bio:")
        sections.append(bios[0][:300])

    # Include GBP photos if available — Stitch can use them for visual reference
    photo_urls = _get_gbp_photos(lead)
    if photo_urls:
        sections.append("")
        sections.append("Real business photos (use these for hero image, about section, gallery):")
        for i, url in enumerate(photo_urls[:5]):
            sections.append(f"- Photo {i+1}: {url}")
        sections.append("Use these actual photos instead of AI-generated placeholder images.")

    sections.extend([
        "",
        "Required sections:",
        "- Hero with business name and a compelling tagline",
        "- About section describing who they are",
        "- Services/offerings section (from their actual posts, not invented)",
        "- Contact section with real address, phone (clickable tel: link), and social media links",
        f"- Footer: '© 2026 {lead.business_name}. All rights reserved.' and "
        f"'Powered by SiteSmyth — Want a site like this? Call {cfg.contact_phone}'",
        "",
        "Design rules:",
        "- Choose a color palette that fits their industry and personality",
    ])
    if photo_urls:
        sections.append("- Use the real business photos provided above for hero/about/gallery sections")
        sections.append("- Match the color palette to the vibe of the photos")
    else:
        sections.append("- Use CSS gradients and decorative elements for visual interest — NO stock photos")
    sections.extend([
        "- Mobile-responsive design",
        "- Professional and polished — this is a sales demo to convince them to buy",
        "- Include inline SVG icons for social media links (Facebook, Instagram)",
        "- NEVER invent services, prices, menu items, or events not in the description",
    ])

    return "\n".join(sections)


def _swap_photos(html: str, lead: Lead) -> str:
    """Replace Stitch's AI-generated placeholder images with real GBP photos."""
    import re
    photos = _get_gbp_photos(lead)
    if not photos:
        return html

    ai_pattern = re.compile(
        r'(src\s*=\s*["\'])https://lh3\.googleusercontent\.com/aida-public/[^"\']+(["\'])'
    )
    matches = list(ai_pattern.finditer(html))
    if not matches:
        return html

    replacements = 0
    for match in matches:
        if replacements >= len(photos):
            break
        old = match.group(0)
        new = f'{match.group(1)}{photos[replacements]}{match.group(2)}'
        html = html.replace(old, new, 1)
        replacements += 1

    if replacements:
        log.info("  Swapped %d AI images with real GBP photos", replacements)

    return html


def _get_gbp_photos(lead: Lead) -> list[str]:
    """Return Google Business Profile photo URLs if stored on the lead."""
    if not lead.gbp_photo_urls:
        return []
    try:
        urls = json.loads(lead.gbp_photo_urls)
        return [u for u in urls if isinstance(u, str) and u.startswith("http")]
    except (json.JSONDecodeError, TypeError):
        return []


def _generate_with_stitch(prompt: str, access_token: str) -> str:
    """Call Stitch SDK to generate a screen and download its HTML."""
    # Import here to avoid requiring node deps at module level
    import subprocess as sp

    # Write a small Node script that does the generation
    script = f"""
import {{ StitchToolClient }} from "@google/stitch-sdk";

const client = new StitchToolClient({{
  accessToken: {json.dumps(access_token)},
  projectId: "gen-lang-client-0901380994",
}});

try {{
  const proj = await client.callTool("create_project", {{ title: "SiteSmyth Build" }});
  const projId = proj?.name?.match(/projects\\/(\\d+)/)?.[1];

  const result = await client.callTool("generate_screen_from_text", {{
    projectId: projId,
    prompt: {json.dumps(prompt)},
    deviceType: "DESKTOP",
    modelId: "GEMINI_3_FLASH",
  }});

  const screens = result?.outputComponents
    ?.flatMap(c => c?.design?.screens || []) || [];

  if (screens.length === 0) {{
    console.error("ERROR: No screens generated");
    process.exit(1);
  }}

  const htmlUrl = screens[0].htmlCode?.downloadUrl;
  if (!htmlUrl) {{
    console.error("ERROR: No HTML URL in response");
    process.exit(1);
  }}

  const resp = await fetch(htmlUrl);
  const html = await resp.text();
  process.stdout.write(html);
}} catch (err) {{
  console.error("ERROR:", err.message);
  process.exit(1);
}} finally {{
  await client.close();
}}
"""
    import tempfile
    project_root = Path(__file__).resolve().parent.parent.parent

    # Ensure Stitch SDK is installed
    stitch_pkg = project_root / "node_modules" / "@google" / "stitch-sdk"
    if not stitch_pkg.exists():
        log.info("  Installing @google/stitch-sdk...")
        sp.run(
            ["npm", "init", "-y"],
            capture_output=True, cwd=str(project_root), timeout=15,
        )
        sp.run(
            ["npm", "install", "@google/stitch-sdk"],
            capture_output=True, cwd=str(project_root), timeout=60,
        )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mjs", dir=str(project_root),
        prefix=".stitch_tmp_", delete=False
    ) as f:
        f.write(script)
        script_path = Path(f.name)

    try:
        result = sp.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=300,
            cwd=str(project_root),
        )
        if result.returncode != 0:
            err = result.stderr.strip()
            log.error("  Stitch generation failed: %s", err[:500])
            raise RuntimeError(f"Stitch generation failed: {err[:200]}")

        html = result.stdout
        if not html or len(html) < 100:
            raise RuntimeError("Stitch returned empty or too-short HTML")

        return html
    finally:
        script_path.unlink(missing_ok=True)


def _inject_seo(html: str, lead: Lead, cfg: Config) -> str:
    """Inject JSON-LD, Open Graph, SiteSmyth branding, and language toggle."""
    seo_block = _build_seo_block(lead, cfg)

    if "</head>" in html:
        html = html.replace("</head>", seo_block + "\n</head>", 1)

    if "sitesmyth" not in html.lower():
        branding = (
            f'\n<div style="text-align:center;padding:12px;background:#111;color:#888;font-size:12px;">'
            f'Powered by <a href="https://sitesmyth.com" style="color:#D4AF37;">SiteSmyth</a>'
            f' &mdash; Want a site like this? Call {cfg.contact_phone}</div>\n'
        )
        html = html.replace("</body>", branding + "</body>", 1)

    if _should_add_lang_toggle(lead):
        html = _inject_lang_toggle(html)

    return html


def _should_add_lang_toggle(lead: Lead) -> bool:
    """Detect if business likely serves Spanish-speaking customers."""
    spanish_categories = {"mexican", "taqueria", "michoacan", "latino", "hispanic",
                          "panaderia", "carniceria", "pupuseria", "salvadoran"}
    name_lower = (lead.business_name or "").lower()
    cat_lower = (lead.category or "").lower()
    combined = name_lower + " " + cat_lower
    return any(kw in combined for kw in spanish_categories)


def _inject_lang_toggle(html: str) -> str:
    """Inject an ES/EN toggle that redirects through Google Translate for Spanish."""
    toggle_block = """
<style>
#smyth-lang-toggle {
  position: fixed; bottom: 24px; right: 24px; z-index: 99999;
  display: flex; gap: 0; border-radius: 999px; overflow: hidden;
  box-shadow: 0 6px 24px rgba(0,0,0,0.5); font-family: system-ui, -apple-system, sans-serif;
  border: 2px solid rgba(212,175,55,0.4);
}
#smyth-lang-toggle button {
  border: none; padding: 12px 22px; font-size: 14px; font-weight: 800;
  cursor: pointer; text-transform: uppercase; letter-spacing: 0.1em;
  transition: all 0.2s ease;
}
.smyth-lang-active { background: #D4AF37 !important; color: #111 !important; }
.smyth-lang-inactive { background: #1a1a1a !important; color: #999 !important; }
.smyth-lang-inactive:hover { background: #2a2a2a !important; color: #fff !important; }
</style>
<div id="smyth-lang-toggle">
  <button class="smyth-lang-active" onclick="smythLang('en')">EN</button>
  <button class="smyth-lang-inactive" onclick="smythLang('es')">ES</button>
</div>
<script>
(function(){
  var isTranslated = window.location.hostname.indexOf('translate.goog') > -1;
  var btns = document.querySelectorAll('#smyth-lang-toggle button');
  if (isTranslated) {
    btns[0].className = 'smyth-lang-inactive';
    btns[1].className = 'smyth-lang-active';
  }
  window.smythLang = function(lang) {
    if (lang === 'es' && !isTranslated) {
      var u = encodeURIComponent(window.location.href);
      window.location.href = 'https://translate.google.com/translate?sl=en&tl=es&u=' + u;
    } else if (lang === 'en' && isTranslated) {
      var orig = document.querySelector('a.goog-logo-link');
      if (orig) { orig.click(); return; }
      var clean = window.location.href.replace(/translate[.]google[.]com[/]translate.*?u=/, '');
      window.location.href = decodeURIComponent(clean);
    }
  };
})();
</script>"""

    if "</body>" in html:
        html = html.replace("</body>", toggle_block + "\n</body>", 1)
    return html


def _build_seo_block(lead: Lead, cfg: Config) -> str:
    """Build JSON-LD + Open Graph meta tags."""
    same_as = []
    if lead.facebook_url:
        same_as.append(lead.facebook_url)
    if lead.instagram_handle:
        same_as.append(f"https://instagram.com/{lead.instagram_handle}")

    json_ld = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": lead.business_name,
        "url": f"https://{lead.slug}.{cfg.sitesmyth_domain}",
    }
    if lead.address:
        parts = lead.address.split(",")
        json_ld["address"] = {
            "@type": "PostalAddress",
            "streetAddress": parts[0].strip() if parts else lead.address,
            "addressLocality": lead.city or "",
            "addressRegion": lead.state or "",
        }
    if lead.phone:
        json_ld["telephone"] = lead.phone
    if same_as:
        json_ld["sameAs"] = same_as

    desc = f"{lead.business_name} in {lead.city or 'your area'}, {lead.state or ''}. {lead.category or 'Local business'}."

    lines = [
        f'<meta property="og:title" content="{lead.business_name}">',
        f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:url" content="https://{lead.slug}.{cfg.sitesmyth_domain}">',
        '<meta property="og:type" content="website">',
        f'<script type="application/ld+json">{json.dumps(json_ld, indent=2)}</script>',
    ]
    return "\n".join(lines)
