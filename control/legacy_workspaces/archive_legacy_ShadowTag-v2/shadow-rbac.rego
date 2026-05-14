package rbac_shadows

violation[{"msg": msg}] {
  binding := input.review.object.rules[_]
  resources := ["secrets", "pods/exec"]
  resource in resources
  verbs := ["*"]
  verb in binding.verbs
  msg := "Wildcard verbs on privileged resources"
}
