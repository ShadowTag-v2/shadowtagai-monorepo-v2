package hpa_pennal

violation[{"msg": msg}] {
  hpa := input.review.object
  hpa.spec.minReplicas > 5
  msg := "Min replicas capped at 5 for troops"
}

violation[{"msg": msg}] {
  hpa.spec.maxReplicas > 100
  msg := "Max replicas 100 for penal safety"
}
