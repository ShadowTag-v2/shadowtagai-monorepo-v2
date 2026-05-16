package rbac_multi_tenant

deny[msg] {
  ns := input.review.object.metadata.namespace
  tenant_ns := ["tenant-a", "penal-colony"]
  not ns in tenant_ns
  msg := "Cross-tenant RBAC violation"
}

allow if {
  input.review.userInfo.username in input.allowed_troops
  input.request.namespace == "penal-colony-monkeys"
}
