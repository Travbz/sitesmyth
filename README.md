# SiteSmyth

Find local businesses without websites, build demo sites from their social/Google content, host them at `*.sitesmyth.com`, and run cold outreach.

Two ways to build:
- **Automated pipeline** — discover → scrape → generate → host → outreach (bulk, cold leads)
- **Manual build** — you give a business's info to the agent and it builds a polished demo (warm leads, full control). See [docs/MANUAL_BUILD_WORKFLOW.md](docs/MANUAL_BUILD_WORKFLOW.md).

```
Discovery (Apify/Google Maps) → Scrape (FB + IG) → Generate (Gemini / Google Stitch) → Host (Cloudflare R2) → Outreach (Email)
```

---

## Prerequisites

Install these before setup:

| Tool | Version | Why |
|------|---------|-----|
| **Python** | 3.11+ | Core app |
| **Node + npm** | 18+ | Google Stitch builder runs JS at build time |
| **git** | any | Clone repo |
| `wrangler` (Cloudflare CLI) | latest | Deploy the hosting Worker — `npm i -g wrangler` |
| `terraform` | latest | Optional: provision Cloudflare infra — see [docs/SETUP.md](docs/SETUP.md) |

You also need a **domain** (e.g. `sitesmyth.com`) on Cloudflare to host live sites. Domain/DNS/Worker/R2 setup is fully documented in [docs/SETUP.md](docs/SETUP.md).

---

## API Providers (accounts you must create)

Sign up and grab a key from each. Most have free tiers; scraping and email cost money at volume.

| Service | Used for | Get a key | Cost |
|---------|----------|-----------|------|
| **Apify** | Google Maps discovery, Facebook + Instagram scraping | [apify.com](https://apify.com) → Settings → Integrations | Free tier, then pay-as-you-go |
| **Google Gemini** | AI content generation, vision | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Free tier available |
| **Google Maps / Places** | Discovery (optional alternative to Apify) | [console.cloud.google.com](https://console.cloud.google.com) → enable Places API | Free credit, then usage-based |
| **Cloudflare** | R2 storage + Worker hosting | [dash.cloudflare.com](https://dash.cloudflare.com) → R2 + API Tokens | R2 free tier (10GB) |
| **Resend** | Cold email delivery | [resend.com](https://resend.com) → API Keys | Free tier (3k emails/mo) |
| **Twilio** *(optional, Phase 2)* | SMS outreach | [twilio.com](https://twilio.com) | Pay-as-you-go |

Put every key in your `.env` — see [.env.example](.env.example) for the exact variable names.

---

## Setup

```bash
git clone git@github.com:Travbz/sitesmyth.git
cd sitesmyth

# Python deps (use a virtualenv)
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Config
cp .env.example .env
# Fill in the keys from the table above

# Database
alembic upgrade head
```

Verify it installed:

```bash
sitesmyth status
```

---

## Commands

| Command | Description |
|---------|-------------|
| `sitesmyth discover --zip 45202 --categories "restaurants"` | Find businesses without websites |
| `sitesmyth scrape --all-pending` | Scrape Facebook/Instagram content |
| `sitesmyth generate --all-scraped` | Generate demo sites |
| `sitesmyth upload --all-generated` | Upload to Cloudflare R2 |
| `sitesmyth outreach --all-hosted --channel email` | Send cold emails |
| `sitesmyth run --zip 45202 --limit 5` | Full automated pipeline |
| `sitesmyth add-lead --name "..." --category "..." --city "..." --state "..."` | Add a lead manually |
| `sitesmyth add-photos --lead-id <ID> "<url>" ...` | Attach Google photos for theming |
| `sitesmyth status` | Pipeline stats |
| `sitesmyth upload-landing` | Deploy landing page to sitesmyth.com |

For the manual, agent-driven build flow see [docs/MANUAL_BUILD_WORKFLOW.md](docs/MANUAL_BUILD_WORKFLOW.md).

---

## Hosting (Cloudflare Workers + R2)

Full walkthrough — domain, DNS, Terraform, tunnel — in [docs/SETUP.md](docs/SETUP.md). Short version:

1. Add your domain to Cloudflare (move nameservers from registrar)
2. Create R2 bucket `sitesmyth-demos`
3. Add wildcard route `*.sitesmyth.com` to the Worker
4. Deploy: `cd infrastructure && wrangler deploy`
5. Upload sites via `sitesmyth upload` (boto3 S3 API → R2)

---

## Outreach Safety

- `outreach_log` has `UNIQUE(lead_id, channel, sequence_number)` — prevents double-sends
- `suppressions` table tracks unsubscribes/bounces — checked before every send
- Use `sitesmyth outreach --all-hosted` to respect dedup and suppression

---

## Docs

- [docs/SETUP.md](docs/SETUP.md) — domain → Cloudflare → Workers + R2 (Terraform)
- [docs/MANUAL_BUILD_WORKFLOW.md](docs/MANUAL_BUILD_WORKFLOW.md) — agent-driven manual builds
- [docs/ARCHITECTURE_OPTIONS.md](docs/ARCHITECTURE_OPTIONS.md) — design trade-offs
- [docs/GEO_SEO_INTEGRATION.md](docs/GEO_SEO_INTEGRATION.md) — SEO/GEO audit plan
- [docs/GEMINI_BUILDER_ROADMAP.md](docs/GEMINI_BUILDER_ROADMAP.md) — builder roadmap
