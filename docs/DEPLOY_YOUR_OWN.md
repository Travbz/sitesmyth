# Deploy Your Own SiteSmyth

This repo is wired for the `sitesmyth.com` domain, but nothing here is locked to
it. Follow this guide to stand up the same hosting (Cloudflare Worker + R2 +
wildcard subdomains) on **your own domain and your own Cloudflare account**.

You can drive the whole thing from an AI agent (Claude) — see
[Path C: Cloudflare MCP](#path-c-agent-driven-with-the-cloudflare-mcp-server).

---

## What you end up with

```
yourdomain.com          → landing page          (R2: _marketing/)
www.yourdomain.com      → landing page
{anything}.yourdomain.com → a hosted demo site  (R2: sites/{anything}/)
```

A single Cloudflare Worker reads the subdomain off each request and serves the
matching folder out of one R2 bucket.

---

## Prerequisites (one-time)

1. **A domain.** Buy one anywhere (Cloudflare Registrar, Namecheap, GoDaddy…).
2. **A Cloudflare account** — free plan is enough. [dash.cloudflare.com](https://dash.cloudflare.com)
3. **Add your domain to Cloudflare** and point your registrar's nameservers at
   the two Cloudflare gives you. Wait until the zone shows **Active**.
   Full walkthrough (incl. GoDaddy) is in [SETUP.md](SETUP.md) Part 1.
4. **A Cloudflare API token.** Dashboard → My Profile → API Tokens → Create Token.
   Give it: `Account → Workers Scripts → Edit`, `Account → Workers R2 Storage →
   Edit`, and `Zone → Workers Routes → Edit` for your zone. Save the token.
5. **Your Account ID** — Cloudflare dashboard right sidebar, or `wrangler whoami`.

> Everything you change to make this yours: the **domain**, the **R2 bucket
> name**, and the **Worker name**. They live in `infrastructure/wrangler.toml`,
> `terraform/terraform.tfvars`, and your `.env`.

---

## Pick a path

| Path | Best when | Sets up infra | Deploys Worker |
|------|-----------|---------------|----------------|
| **A. Wrangler in CI** | You want push-to-deploy from GitHub | You (once, by hand) | GitHub Actions |
| **B. Terraform** | You want bucket + worker + routes + DNS as code | Terraform | Terraform |
| **C. Cloudflare MCP** | You want an AI agent to do it conversationally | Agent | Agent / wrangler |

A and B are not mutually exclusive — many people provision once with Terraform
(Path B) then let CI redeploy the Worker on every push (Path A).

---

## Path A: Wrangler in GitHub Actions (push-to-deploy)

The repo already ships `.github/workflows/deploy.yml`. It runs `wrangler deploy`
on every push that touches `infrastructure/`, and **no-ops** if you haven't added
Cloudflare secrets — so it won't break anyone's fork.

### 1. Create the R2 bucket (once)

```bash
npm i -g wrangler
wrangler login                      # opens browser
wrangler r2 bucket create yourdomain-demos
```

### 2. Point the config at your domain

Edit [`infrastructure/wrangler.toml`](../infrastructure/wrangler.toml):

```toml
name = "yourdomain-worker"

[vars]
DOMAIN = "yourdomain.com"           # <- the Worker reads this

[[r2_buckets]]
binding = "R2"
bucket_name = "yourdomain-demos"    # <- must match the bucket you created

# Uncomment AFTER the domain is Active on Cloudflare:
[[routes]]
pattern = "*.yourdomain.com/*"
zone_name = "yourdomain.com"
[[routes]]
pattern = "yourdomain.com/*"
zone_name = "yourdomain.com"
[[routes]]
pattern = "www.yourdomain.com/*"
zone_name = "yourdomain.com"
```

### 3. Add a wildcard DNS record

Cloudflare dashboard → your domain → DNS → Add record:

- Type `CNAME`, Name `*`, Target `yourdomain.com`, **Proxied (orange cloud) ON**.

(Terraform does this for you in Path B.)

### 4. Add GitHub repo secrets

Repo → Settings → Secrets and variables → Actions → New repository secret:

- `CLOUDFLARE_API_TOKEN` — the token from Prerequisites step 4
- `CLOUDFLARE_ACCOUNT_ID` — your account ID

### 5. Deploy

Push any change under `infrastructure/`, or trigger manually: Actions →
**Deploy Worker** → Run workflow. CI runs `wrangler deploy` and your Worker goes
live. First deploy locally to sanity-check:

```bash
cd infrastructure && wrangler deploy
```

---

## Path B: Terraform (infra as code)

Terraform creates the R2 bucket, Worker, routes, and wildcard DNS in one shot.
Config lives in [`terraform/`](../terraform).

### 1. Fill in your values

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
cloudflare_account_id = "your_account_id"
cloudflare_api_token  = "your_api_token"
domain                = "yourdomain.com"
worker_name           = "yourdomain-worker"   # optional override
bucket_name           = "yourdomain-demos"     # optional override
```

> `terraform.tfvars` holds your token — it is gitignored by `*.tfvars`-style
> rules. **Never commit it.** Double-check before pushing.

### 2. Apply

```bash
terraform init
terraform plan      # review what it will create
terraform apply
```

That provisions everything, including the `DOMAIN` binding the Worker reads and
the proxied wildcard DNS record. Output: your Worker + routes live.

### 3. (Optional) Terraform in CI

To run `terraform apply` from GitHub Actions, store the same values as repo
secrets and use `hashicorp/setup-terraform`. Use a remote state backend (R2, S3,
or Terraform Cloud) so CI runs share state. Ask the agent to scaffold a
`terraform.yml` workflow when you're ready — it's a small addition to what's here.

---

## Path C: Agent-driven with the Cloudflare MCP server

If you'd rather just *talk to Claude* and have it do the Cloudflare work, connect
the official Cloudflare MCP servers. Then the agent can create buckets, inspect
Workers, read logs, and manage DNS through tool calls instead of you running CLI
commands.

### 1. Add the MCP servers

Cloudflare publishes remote MCP servers (no local install). The relevant ones:

- **Workers Bindings** — manage Workers, R2, KV, D1 — `https://bindings.mcp.cloudflare.com/sse`
- **Workers Observability** — read Worker logs/analytics — `https://observability.mcp.cloudflare.com/sse`

Add to Claude Code:

```bash
claude mcp add --transport sse cloudflare-bindings https://bindings.mcp.cloudflare.com/sse
claude mcp add --transport sse cloudflare-observability https://observability.mcp.cloudflare.com/sse
```

(Or for Claude Desktop, add them under `mcpServers` in the desktop config and
restart.) First use opens a browser to OAuth into your Cloudflare account, so the
agent acts as *you* — no API token to paste.

> Browse the full list at [github.com/cloudflare/mcp-server-cloudflare](https://github.com/cloudflare/mcp-server-cloudflare).

### 2. Let the agent drive

Once connected, prompts like these work:

- "Create an R2 bucket named `yourdomain-demos`."
- "Update `infrastructure/wrangler.toml` for `yourdomain.com` and deploy the Worker."
- "Show me the last 50 Worker errors." (observability server)

The agent still uses `wrangler deploy` (Path A) for the actual Worker push —
MCP handles the account-side resources and inspection. Keep the API token /
secrets from Path A around for the deploy step.

---

## After it's live: build and host a site

Hosting is only the platform. To put an actual demo site up:

```bash
# from the repo root, with .env filled in (see ../README.md)
sitesmyth add-lead --name "Joe's Diner" --category "Restaurant" --city "Denver" --state "CO"
sitesmyth generate --lead-id 1
sitesmyth upload --lead-id 1          # pushes to R2: sites/joes-diner/
```

Then `joes-diner.yourdomain.com` serves it. Deploy the landing page with
`sitesmyth upload-landing` (writes to `_marketing/`).

Branding/links still say "SiteSmyth" in templates and emails — search the repo
for `sitesmyth.com` to rebrand (see list below).

---

## Files that still reference the original brand/domain

These are cosmetic (links, footer text, contact info) — change them when you
rebrand, not required for hosting to work:

- `sitesmyth/config.py` — `contact_email`, default domain (override via `.env`: `SITESMYTH_DOMAIN`, `CONTACT_EMAIL`)
- `sitesmyth/generator/templates/*.html` — "Powered by SiteSmyth" footer
- `sitesmyth/generator/stitch_builder.py` — footer link
- `sitesmyth/outreach/email_sender.py` — outreach copy + unsubscribe URL
- `landing/src/layouts/Layout.astro` — canonical URL, OG image
- `infrastructure/tracking.js` — analytics beacon URL

Set these in `.env` where possible (`SITESMYTH_DOMAIN`, `CONTACT_EMAIL`,
`CONTACT_PHONE`) so you don't have to fork the code.

---

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `Site not found` on every URL | Bucket empty (upload a site) or `bucket_name` mismatch between wrangler.toml and the real bucket |
| Subdomain serves the landing page | `DOMAIN` var not set / wrong — check `[vars]` in wrangler.toml |
| Routes won't attach | Domain not yet **Active** on Cloudflare, or token lacks `Zone → Workers Routes → Edit` |
| CI deploy skipped | `CLOUDFLARE_API_TOKEN` secret missing (by design — add it) |
| SSL error on `*.yourdomain.com` | Free plan covers one wildcard level; ensure the wildcard DNS record is **proxied** |
