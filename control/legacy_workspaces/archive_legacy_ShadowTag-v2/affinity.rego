package pod_affinity

required_affinity[{"msg": msg}] {
  pod := input.review.object
  not pod.spec.affinity.podAntiAffinity
  msg := "Anti-affinity required for troop isolation"
}

preferred_affinity[{"msg": msg}] {
  pod := input.review.object
  pod.spec.affinity.nodeAffinity.preferredDuringSchedulingIgnoredDuringExecution[0].preference.matchExpressions[0].values[_] != "penal-secure"
  msg := "Preferred penal-secure nodes"
}
