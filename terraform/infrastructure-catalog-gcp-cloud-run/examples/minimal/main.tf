module "service" {
  source       = "../../modules/cloud-run-service"
  project_id   = "my-project"
  region       = "us-central1"
  service_name = "hello-world"
  image        = "us-docker.pkg.dev/cloudrun/container/hello"
}

output "url" { value = module.service.url }
