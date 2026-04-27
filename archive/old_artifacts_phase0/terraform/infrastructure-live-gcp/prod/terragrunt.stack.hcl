# Terragrunt Stack — Production
# Deploys all production services in us-central1 atomically
# Usage: cd infrastructure-live-gcp/prod && terragrunt stack run plan

unit "counselconduit" {
  source = "./us-central1/counselconduit"
}

unit "kovelai" {
  source = "./us-central1/kovelai"
}

unit "monitoring" {
  source     = "./us-central1/monitoring"
  depends_on = [unit.counselconduit, unit.kovelai]
}
