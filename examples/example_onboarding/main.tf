module "api_proxy_onboarding" {
  source      = "../../modules/apigee_onboarding"
  input_json  = "./input.json"
  apigee_org  = "my-apigee-org"
  apigee_env  = "test"
}
