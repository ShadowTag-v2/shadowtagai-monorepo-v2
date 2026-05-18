unit "cloud-run" {
  source = "git::https://github.com/ShadowTag-v2/infrastructure-catalog-gcp-cloud-run.git//modules/cloud-run-service?ref=v1.2.0"
  values = { service_name = "api", image = "us-central1-docker.pkg.dev/shadowtag-omega-v4/api:latest" }
}

unit "cloud-deploy" {
  source = "git::https://github.com/ShadowTag-v2/infrastructure-catalog-gcp-cloud-run.git//modules/cloud-deploy-canary-pipeline?ref=v1.2.0"
  values = { name = "api", cloud_run_service_name = dependency.cloud-run.outputs.service_name }
}
