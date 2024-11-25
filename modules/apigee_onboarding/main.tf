terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }

  required_version = ">= 1.5.7"
}

provider "google" {
  credentials = file(var.google_credentials)
  project     = var.google_project
  region      = var.google_region
}

# Null resource to trigger the JSON-to-Proxy conversion script
resource "null_resource" "convert_json_to_proxy" {
  provisioner "local-exec" {
    command = "python3 ../../scripts/json_to_proxy.py --input ${var.input_json} --output ../artifacts"
  }
}

# Loop over generated artifacts and deploy them as Apigee proxies
resource "google_apigee_proxy" "api_proxy" {
  for_each = fileset("../artifacts", "*.zip")

  org        = var.apigee_org
  name       = each.key
  bundle     = "../artifacts/${each.key}.zip"
  environments = var.apigee_environments
}

# Create Apigee API product
resource "google_apigee_api_product" "api_product" {
  for_each = var.products

  name        = each.value.name
  display_name = each.value.display_name
  description = each.value.description
  environments = var.apigee_environments
  proxies      = [for p in google_apigee_proxy.api_proxy : p.name]
  quotas {
    limit    = each.value.quota_limit
    interval = each.value.quota_interval
    timeunit = each.value.quota_timeunit
  }
}

