# SiteSmyth Setup Guide

From GoDaddy domain to live Cloudflare Workers + R2, with Terraform and an optional tunnel.

---

## Overview

```text
GoDaddy (registrar)  →  Cloudflare (DNS + Workers + R2)  →  *.sitesmyth.com
                              ↑
                    Terraform manages it all
```

---

## Part 1: Add Domain to Cloudflare (Manual, One-Time)

You keep the domain registered at GoDaddy but move **DNS** to Cloudflare.

### 1.1 Add site in Cloudflare

1. Go to [cloudflare.com](https://cloudflare.com) → Sign up or log in
2. **Add a site** → enter `sitesmyth.com`
3. Choose **Free** plan
4. Cloudflare will scan existing DNS from GoDaddy (or show a placeholder if the domain is new)
5. On the nameserver page, note your two nameservers, e.g.:
   - `ken.ns.cloudflare.com`
   - `mira.ns.cloudflare.com`

### 1.2 Point GoDaddy to Cloudflare

1. Log in to [godaddy.com](https://godaddy.com)
2. **My Products** → Domains → `sitesmyth.com` → **DNS** (or **Manage**)
3. Find **Nameservers** → **Change**
4. Choose **Enter my own nameservers**
5. Replace with the two Cloudflare nameservers
6. Save

### 1.3 Wait and verify

- Propagation: often 15 minutes–2 hours, sometimes up to 48 hours
- Check at [whatsmydns.net](https://whatsmydns.net) or Cloudflare dashboard when DNS is “Active”

---

## Part 2: Terraform (Cloudflare Resources)

Terraform manages the zone, R2 bucket, Worker, routes, and optional tunnel.

### 2.1 Prerequisites

```bash
# Install Terraform (macOS)
brew install terraform

# Or: https://developer.hashicorp.com/terraform/install
```

### 2.2 Get Cloudflare credentials

1. **Account ID**: Cloudflare dashboard → right sidebar or **Workers & Pages** → Account ID
2. **API Token**: [API Tokens](https://dash.cloudflare.com/profile/api-tokens) → Create Token → **Edit zone DNS** + **Workers Scripts** + **R2** + **Cloudflare Tunnel** (or use a template for full account access)

### 2.3 Terraform layout

The `terraform/` directory contains:

```text
terraform/
├── main.tf                  # Zone, R2, Worker, routes
├── tunnel.tf                 # Optional: Cloudflare Tunnel (commented)
├── variables.tf
├── outputs.tf
├── terraform.tfvars.example  # Copy to terraform.tfvars (gitignored)
└── terraform.tfvars          # Your secrets (gitignored)
```

### 2.4 Terraform files

**`terraform/variables.tf`**

```hcl
variable "cloudflare_account_id" {
  type        = string
  description = "Cloudflare account ID"
}

variable "cloudflare_api_token" {
  type        = string
  sensitive   = true
  description = "Cloudflare API token"
}

variable "domain" {
  type    = string
  default = "sitesmyth.com"
}
```

The repo includes `terraform/main.tf`, `variables.tf`, `outputs.tf`. Create your vars file and apply:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with cloudflare_account_id and cloudflare_api_token

terraform init
terraform plan
terraform apply
```

---

## Part 3: Cloudflare Tunnel (Optional)

Use a tunnel if you want to expose a local service (e.g. API, dev server) without opening ports.

### 3.1 When to use

- Local dev API that the landing page or pipeline calls
- Dashboard or admin UI
- Raspberry Pi or other machine running the pipeline behind a firewall

### 3.2 Create tunnel with Terraform

Add to `terraform/main.tf` required_providers:

```hcl
random = {
  source  = "hashicorp/random"
  version = "~> 3"
}
```

**`terraform/tunnel.tf`** (uncomment the block in the repo, or add):

```hcl
# Cloudflare Tunnel (cloudflared)
resource "cloudflare_tunnel" "sitesmyth" {
  account_id = var.cloudflare_account_id
  name       = "sitesmyth-tunnel"
  secret     = base64encode(random_password.tunnel_secret.result)
}

resource "random_password" "tunnel_secret" {
  length  = 32
  special = false
}

# Route tunnel traffic to your service
resource "cloudflare_tunnel_config" "sitesmyth" {
  account_id = var.cloudflare_account_id
  tunnel_id  = cloudflare_tunnel.sitesmyth.id

  config {
    ingress_rule {
      hostname = "api.sitesmyth.com"
      service  = "http://localhost:8000"
    }
    ingress_rule {
      hostname = var.domain
      service  = "http_status:404"
    }
    ingress_rule {
      service = "http_status:404"
    }
  }
}

# CNAME for tunnel
resource "cloudflare_record" "tunnel_api" {
  zone_id = data.cloudflare_zone.sitesmyth.id
  name   = "api"
  type   = "CNAME"
  content = "${cloudflare_tunnel.sitesmyth.id}.cfargotunnel.com"
  ttl    = 1
  proxied = true
}

output "tunnel_id" {
  value     = cloudflare_tunnel.sitesmyth.id
  sensitive = true
}

output "tunnel_token" {
  value     = cloudflare_tunnel.sitesmyth.tunnel_token
  sensitive = true
}
```

### 3.3 Run cloudflared locally

After `terraform apply`, run the tunnel:

```bash
# Install cloudflared
brew install cloudflared

# Use the token from terraform output
terraform output -raw tunnel_token | cloudflared tunnel run --
```

Traffic to `api.sitesmyth.com` will go to `http://localhost:8000`.

---

## Part 4: R2 API Credentials (for Python uploader)

The Terraform R2 bucket exists, but the Python `uploader.py` needs S3-style credentials.

1. Cloudflare dashboard → **R2** → **Manage R2 API Tokens**
2. Create token with **Object Read & Write** for `sitesmyth-sites`
3. Note: **Access Key ID**, **Secret Access Key**
4. Add to `.env`:

```env
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_R2_ACCESS_KEY=...
CLOUDFLARE_R2_SECRET_KEY=...
CLOUDFLARE_R2_BUCKET=sitesmyth-sites
```

Endpoint: `https://<account_id>.r2.cloudflarestorage.com` (uploader uses this automatically).

---

## Part 5: Gemini API Key (content generation)

Gemini Flash powers the site generator — vision analysis, copy writing, image selection.

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with a Google account
3. Click **Get API key** (or use an existing project)
4. Create an API key; copy it
5. Add to `.env`:

```env
GEMINI_API_KEY=your_key_here
# GEMINI_MODEL=gemini-2.0-flash  # optional override
```

Pricing: free tier includes 15 RPM; paid is ~$0.075/1M input tokens. Each site costs roughly $0.001–0.005.

---

## Part 5.5: Google Places API (optional, for discovery)

If you have a Google Cloud API key with the **Places API (New)** enabled, you can use it for discovery instead of Apify. Discovery will use Places if `GOOGLE_MAPS_KEY` is set; otherwise it falls back to Apify.

1. In [Google Cloud Console](https://console.cloud.google.com/), enable **Places API (New)** for your project
2. Create or reuse an API key with Places access
3. Add to `.env`:

```env
GOOGLE_MAPS_KEY=your_key_here
```

Pricing: text search is ~$17 per 1000 requests. A typical `sitesmyth discover` run uses a few dollars depending on categories and pagination.

---

## Part 6: Apify API Token (scraping)

Apify runs the Facebook and Instagram scrapers, and is used for **discovery** only when `GOOGLE_MAPS_KEY` is not set.

1. Go to [apify.com](https://apify.com) → Sign up or log in
2. **Settings** → **Integrations** → **API** (or [apify.com/accounts/integrations](https://console.apify.com/account/integrations))
3. Copy your **Personal API token**
4. Add to `.env`:

```env
APIFY_API_TOKEN=apify_api_...
```

Pricing: $5 free credits; then pay-per-use (~$0.004/place for Maps, ~$0.01/page for Facebook/Instagram). Starter plan ~$49/mo for higher volume.

### Actor IDs (no setup required)

The pipeline uses these Apify actors. You do **not** add or install them — they run automatically when the code calls them:

| Purpose | Actor ID | Used by |
|---------|----------|---------|
| Google Maps (fallback) | `compass/crawler-google-places` | `discover` (only when `GOOGLE_MAPS_KEY` is unset) |
| Facebook posts | `apify/facebook-posts-scraper` | `scrape`, `activity_check` |
| Instagram posts | `apify/instagram-post-scraper` | `scrape`, `activity_check` |

If an actor is deprecated or renamed, search [Apify Store](https://apify.com/store) for alternatives and update the constant in the code (e.g. `FB_POSTS_ACTOR` in `scraper/facebook_scraper.py`).

---

## Part 7: Checklist

| Step | Action |
|------|--------|
| 1 | Add `sitesmyth.com` to Cloudflare |
| 2 | Update GoDaddy nameservers to Cloudflare |
| 3 | Wait for DNS propagation |
| 4 | Copy `terraform.tfvars.example` → `terraform.tfvars`, fill in tokens |
| 5 | `terraform init && terraform apply` |
| 6 | Create R2 API token and add `CLOUDFLARE_R2_ACCESS_KEY`, `CLOUDFLARE_R2_SECRET_KEY` to `.env` |
| 7 | Get Gemini API key from [Google AI Studio](https://aistudio.google.com/), add `GEMINI_API_KEY` |
| 8 | (Optional) Add `GOOGLE_MAPS_KEY` for Places-based discovery; else get Apify token for discovery fallback |
| 9 | Get Apify token from [apify.com](https://apify.com), add `APIFY_API_TOKEN` (required for Facebook/Instagram; optional for discovery if Places is used) |
| 10 | Deploy landing: `cd landing && npm run build` then `sitesmyth upload-landing` |
| 11 | (Optional) Run cloudflared with tunnel token for `api.sitesmyth.com` |

---

## Part 8: GoDaddy Summary

| Where | What |
|-------|------|
| GoDaddy | You keep the domain registration |
| GoDaddy | Change nameservers to Cloudflare |
| Cloudflare | DNS, SSL, Workers, R2, Tunnels |

You do **not** need to add DNS records in GoDaddy for `sitesmyth.com` — Cloudflare manages all records once nameservers are switched.
