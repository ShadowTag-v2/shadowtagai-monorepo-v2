# Staging root — inherits from parent
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}
