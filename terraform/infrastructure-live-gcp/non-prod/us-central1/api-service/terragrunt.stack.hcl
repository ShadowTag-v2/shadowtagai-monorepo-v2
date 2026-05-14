# ZT.1 / Cor.LawTrack API — full stack deploy
# Expand: terragrunt stack generate
# Plan:   terragrunt stack run plan
# Apply:  terragrunt stack run apply

unit "vpc-connector" {
  source = "git::https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git//terraform/infrastructure-catalog-gcp-cloud-run/modules/cloud-run-vpc-connector?ref=main"
  path   = "vpc-connector"
  values = {
    project_id  = "shadowtag-omega-v4"
    region      = "us-central1"
    name        = "private-run-nonprod"
    subnet_name = "default"
  }
}

unit "cloud-run" {
  source = "git::https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git//terraform/infrastructure-catalog-gcp-cloud-run/modules/cloud-run-service?ref=main"
  path   = "cloud-run"
  values = {
    project_id            = "shadowtag-omega-v4"
    region                = "us-central1"
    service_name          = "lawtrack-api-nonprod"
    image                 = "us-central1-docker.pkg.dev/shadowtag-omega-v4/lawtrack/api:latest"
    service_account_email = "lawtrack-api-sa@shadowtag-omega-v4.iam.gserviceaccount.com"
    min_instances         = 0
    max_instances         = 5
    vpc_connector_id      = dependency.vpc-connector.outputs.id
    vpc_egress            = "PRIVATE_RANGES_ONLY"
    cloud_sql_instances   = ["shadowtag-omega-v4:us-central1:lawtrack-db-primary"]
    secrets = [
      { env_var_name = "DB_PASS", secret_id = "db-password" }
    ]
    env_vars = { ENVIRONMENT = "non-prod" }
  }
  depends_on = ["vpc-connector"]
}

unit "canary" {
  source = "git::https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git//terraform/infrastructure-catalog-gcp-cloud-run/modules/cloud-deploy-canary-pipeline?ref=main"
  path   = "canary"
  values = {
    project_id            = "shadowtag-omega-v4"
    region                = "us-central1"
    name                  = "lawtrack-api-nonprod"
    cloud_run_service_name = dependency.cloud-run.outputs.name
    percentages           = [25, 50, 75]
    verify                = true
  }
  depends_on = ["cloud-run"]
}
