output "zone_id" {
  value = data.cloudflare_zone.sitesmyth.id
}

output "r2_bucket_name" {
  value = cloudflare_r2_bucket.sites.name
}
