package k8spsprestricted

violation[{"msg": msg}] {
  c := input_containers[_]
  not is_run_as_non_root(c)
  msg := "Run as non-root required"
}

is_run_as_non_root(c) {
  c.securityContext.runAsNonRoot == true
}

is_run_as_non_root(c) {
  not c.securityContext.runAsNonRoot
  input.review.object.spec.securityContext.runAsNonRoot == true
}

violation[{"msg": msg}] {
  c := input_containers[_]
  c.securityContext.allowPrivilegeEscalation != false
  msg := "Privilege escalation must be disabled"
}

violation[{"msg": msg}] {
  c := input_containers[_]
  not c.securityContext.capabilities.drop[_] == "ALL"
  msg := "Capabilities must be dropped to ALL"
}

violation[{"msg": msg}] {
  not pod_seccomp_valid
  msg := "Pod-level seccomp profile must be RuntimeDefault"
}

violation[{"msg": msg}] {
  c := input_containers[_]
  not container_seccomp_valid(c)
  msg := "Container-level seccomp profile must be RuntimeDefault"
}

pod_seccomp_valid {
  input.review.object.spec.securityContext.seccompProfile.type == "RuntimeDefault"
}

container_seccomp_valid(c) {
  not c.securityContext.seccompProfile
}

container_seccomp_valid(c) {
  c.securityContext.seccompProfile.type == "RuntimeDefault"
}

input_containers[c] {
  c := input.review.object.spec.containers[_]
}

input_containers[c] {
  c := input.review.object.spec.initContainers[_]
}
