variable "google_credentials" {
  description = "Path to the Google Cloud credentials JSON file"
  type        = string
}

variable "google_project" {
  description = "Google Cloud project ID"
  type        = string
}

variable "google_region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-central1"
}

variable "apigee_org" {
  description = "Apigee organization name"
  type        = string
}

variable "apigee_environments" {
  description = "Apigee environments to deploy proxies to"
  type        = list(string)
}

variable "input_json" {
  description = "Path to the input JSON file containing proxy configuration"
  type        = string
}

variable "products" {
  description = "List of API products to create"
  type = list(object({
    name          = string
    display_name  = string
    description   = string
    quota_limit   = number
    quota_interval = number
    quota_timeunit = string
  }))
  default = []
}
