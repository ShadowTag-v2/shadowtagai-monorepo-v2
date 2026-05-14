package rbac_multi

deny[msg] {
  binding := input.review.object
  troop := binding.metadata.labels["troop"]
  binding.rules[_].resources[_] == "secrets"
  not troop in data.allowed_troops
  msg := "Secrets access denied for rogue troop"
}
