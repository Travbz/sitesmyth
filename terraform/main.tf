terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Zone (must exist — add site at cloudflare.com first)
data "cloudflare_zone" "sitesmyth" {
  name = var.domain
}

# R2 bucket for demo sites + landing page
resource "cloudflare_r2_bucket" "sites" {
  account_id = var.cloudflare_account_id
  name       = "sitesmyth-demos"
  location   = "ENAM"
}

# Worker script
resource "cloudflare_workers_script" "sitesmyth" {
  account_id = var.cloudflare_account_id
  name       = "sitesmyth-worker"
  content    = file("${path.module}/../infrastructure/worker.js")

  r2_bucket_binding {
    name        = "R2"
    bucket_name = cloudflare_r2_bucket.sites.name
  }
}

# Route: *.sitesmyth.com → Worker
resource "cloudflare_worker_route" "wildcard" {
  zone_id     = data.cloudflare_zone.sitesmyth.id
  pattern     = "*.${var.domain}/*"
  script_name = cloudflare_workers_script.sitesmyth.name
}

# Route: sitesmyth.com (root)
resource "cloudflare_worker_route" "root" {
  zone_id     = data.cloudflare_zone.sitesmyth.id
  pattern     = "${var.domain}/*"
  script_name = cloudflare_workers_script.sitesmyth.name
}

# Route: www.sitesmyth.com
resource "cloudflare_worker_route" "www" {
  zone_id     = data.cloudflare_zone.sitesmyth.id
  pattern     = "www.${var.domain}/*"
  script_name = cloudflare_workers_script.sitesmyth.name
}
