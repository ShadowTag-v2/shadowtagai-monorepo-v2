resource "google_vpc_access_connector" "connector" {
  name          = var.name
  region        = var.region
  project       = var.project_id
  machine_type  = var.machine_type
  min_instances = var.min_instances
  max_instances = var.max_instances

  subnet {
    name = var.subnet_name
  }
}
