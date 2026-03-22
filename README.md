# SiteSmyth

Automated pipeline to find local businesses without websites, generate demo sites from their Facebook/Instagram content, host at `*.sitesmyth.com`, and send cold outreach.

## Architecture

```
Discovery (Apify Google Maps) → Scrape (FB + IG) → Generate (Gemini Flash) → Host (R2) → Outreach (Email/IG DM)
```

## Setup

```bash
cd sitesmyth
pip install -e .
cp .env.example .env
# Fill in API keys: APIFY_API_TOKEN, GEMINI_API_KEY, RESEND_API_KEY, etc.
alembic upgrade head
```

## Commands

| Command | Description |
|---------|-------------|
| `sitesmyth discover --zip 45202 --categories "restaurants"` | Find businesses without websites |
| `sitesmyth scrape --all-pending` | Scrape Facebook/Instagram content |
| `sitesmyth generate --all-scraped` | Generate static sites (Gemini Flash) |
| `sitesmyth upload --all-generated` | Upload to Cloudflare R2 |
| `sitesmyth outreach --all-hosted --channel email` | Send cold emails |
| `sitesmyth run --zip 45202 --limit 5` | Full pipeline |
| `sitesmyth status` | Pipeline stats |
| `sitesmyth upload-landing` | Deploy landing page to sitesmyth.com |

## Hosting (Cloudflare Workers + R2)

1. Create R2 bucket `sitesmyth-sites`
2. Add wildcard route `*.sitesmyth.com` to Worker
3. Deploy: `cd infrastructure && wrangler deploy`
4. Upload sites via `sitesmyth upload` (boto3 S3 API to R2)

## Environment

See `.env.example` for required keys. Key services:

- **Apify** — Google Maps, Facebook, Instagram scraping
- **Gemini** — Content generation
- **Resend** — Email delivery
- **Cloudflare** — R2 storage, Worker routing

## Outreach Safety

- `outreach_log` has `UNIQUE(lead_id, channel, sequence_number)` — prevents double-sends
- `suppressions` table tracks unsubscribes/bounces — checked before every send
- Use `sitesmyth outreach --all-hosted` to respect dedup and suppression
