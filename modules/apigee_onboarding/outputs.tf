output "apigee_proxies" {
  description = "List of deployed Apigee proxies"
  value       = [for p in google_apigee_proxy.api_proxy : p.name]
}

output "apigee_products" {
  description = "List of created Apigee API products"
  value       = [for p in google_apigee_api_product.api_product : p.name]
}
