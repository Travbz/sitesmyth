# Optional: Cloudflare Tunnel for api.sitesmyth.com → localhost
# Uncomment and run cloudflared with tunnel_token to expose a local service
# Add to main.tf: required_providers { random = { source = "hashicorp/random", version = "~> 3" } }

# resource "random_password" "tunnel_secret" {
#   length  = 32
#   special = false
# }
#
# resource "cloudflare_tunnel" "sitesmyth" {
#   account_id = var.cloudflare_account_id
#   name       = "sitesmyth-tunnel"
#   secret     = base64encode(random_password.tunnel_secret.result)
# }
#
# resource "cloudflare_tunnel_config" "sitesmyth" {
#   account_id = var.cloudflare_account_id
#   tunnel_id  = cloudflare_tunnel.sitesmyth.id
#
#   config {
#     ingress_rule {
#       hostname = "api.${var.domain}"
#       service  = "http://localhost:8000"
#     }
#     ingress_rule {
#       hostname = var.domain
#       service  = "http_status:404"
#     }
#     ingress_rule {
#       service = "http_status:404"
#     }
#   }
# }
#
# resource "cloudflare_record" "tunnel_api" {
#   zone_id  = data.cloudflare_zone.sitesmyth.id
#   name     = "api"
#   type     = "CNAME"
#   content  = "${cloudflare_tunnel.sitesmyth.id}.cfargotunnel.com"
#   ttl      = 1
#   proxied  = true
# }
#
# output "tunnel_token" {
#   value     = cloudflare_tunnel.sitesmyth.tunnel_token
#   sensitive = true
# }
