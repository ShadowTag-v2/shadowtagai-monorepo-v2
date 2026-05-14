package kubernetes.admission

import future.keywords.in

deny[msg] {
  input.request.kind.kind == "Pod"
  troop := input.request.object.metadata.labels.troop
  not troop in ["trusted_monkey", "hht_leader"]
  msg := sprintf("Unauthorized troop '%s': Penal Colony RBAC violation", [troop])
}

deny[msg] {
  input.request.namespace != "penal-colony"
  msg := "Pods restricted to penal-colony namespace only"
}
