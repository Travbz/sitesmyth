variable "cloudflare_account_id" {
  type        = string
  description = "Cloudflare account ID"
}

variable "cloudflare_api_token" {
  type        = string
  sensitive   = true
  description = "Cloudflare API token (needs Zone, Workers, R2, Tunnel permissions)"
}

variable "domain" {
  type        = string
  default     = "sitesmyth.com"
  description = "Primary domain"
}
