package ns_isolation

deny[msg] {
  input.review.operation == "CREATE"
  ns := input.review.object.metadata.namespace
  requester_ns := input.review.userInfo.namespace
  ns != requester_ns
  msg := sprintf("Namespace cross-access denied: requester is in %q but target is %q", [requester_ns, ns])
}

# NetPol must exist in the target namespace
deny[msg] {
  input.review.operation == "CREATE"
  ns := input.review.object.metadata.namespace
  count({p | p := data.kubernetes.networkpolicies[ns][_]}) == 0
  msg := sprintf("Missing NetworkPolicy isolation in namespace %q", [ns])
}
