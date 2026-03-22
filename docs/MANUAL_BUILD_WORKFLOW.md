# Manual Site Build Workflow

Build demo sites from information you provide directly, bypassing the automated scraping pipeline.

## When to Use

- You have a specific business you want to build for
- The automated scraper finds thin/wrong content
- You want full control over what goes on the site
- You're building a demo for a warm lead, not cold outreach

## Workflow

### 1. Give the Agent Business Info

Tell the agent (Cursor) about the business. Include whatever you have:

- Business name, category, address, phone
- What they do / what services they offer
- Their vibe/personality (rustic, modern, family-friendly, etc.)
- Facebook/Instagram URLs (for social links on the site)
- Google Maps URL (for GBP photo scraping)
- Any specific things you want on the site

The agent will create/update the lead in the DB and build from your description.

### 2. Agent Builds the Site

Two build options:

**Stitch** (default) — Google Stitch generates a polished single-page HTML site.
Best for: quick demos, CSS-only designs, auto language toggle for Spanish businesses.

**Astro + Claude Code** — Full static site with multiple pages, custom components.
Best for: higher-quality builds where the client is warm and you want to impress.

### 3. Review & Iterate

The agent shows you the built site locally. You can:
- Request changes ("make the hero bigger", "change the color scheme", "add a services section")
- The agent edits the HTML directly or regenerates with Stitch `edit_screens`

### 4. Host as Demo

Once approved, the agent uploads to R2:

```
sitesmyth upload --lead-id <ID>
```

Site goes live at `{slug}.sitesmyth.com`.

### 5. Share with Client

Send the demo URL to the business owner for feedback. The site includes SiteSmyth branding and CTA.

## CLI Commands

```bash
# Create a lead manually
sitesmyth add-lead --name "Business Name" --category "Restaurant" \
  --address "123 Main St" --city "Denver" --state "CO" --phone "555-1234"

# Attach GBP photos for design theming
sitesmyth add-photos --lead-id <ID> "https://photo-url-1" "https://photo-url-2"

# Generate and upload
sitesmyth generate --lead-id <ID>
sitesmyth upload --lead-id <ID>

# Or just tell the agent what to build and let it handle everything
```

## What Gets Injected Automatically

Every built site gets:
- JSON-LD structured data (LocalBusiness schema)
- Open Graph meta tags
- SiteSmyth branding + CTA in footer
- `robots.txt` (allows all bots including AI crawlers)
- ES/EN language toggle (auto-detected for Spanish-relevant businesses)
- Real GBP photos swapped in for AI placeholders (when available)

## R2 Hosting Structure

```
sitesmyth-sites/
  sites/{slug}/index.html     # Demo sites
  sites/{slug}/robots.txt
  _marketing/                  # Landing page (sitesmyth.com)
```

Each site is served at `{slug}.sitesmyth.com` via Cloudflare Worker + wildcard DNS.
