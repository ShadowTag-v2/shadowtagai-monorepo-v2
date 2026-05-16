package resource_quota

import future.keywords.in

# Helper to convert K8s CPU strings (e.g. "2", "500m") to float
parse_cpu(str) = res {
  endswith(str, "m")
  res := cast_num(trim_suffix(str, "m")) / 1000
}

parse_cpu(str) = res {
  not endswith(str, "m")
  res := cast_num(str)
}

quotas = {
  "penal-hht": {"cpu": "2"},
  "penal-alpha": {"cpu": "4"}
}

deny[msg] {
  ns := input.review.object.metadata.namespace
  ns_quota := quotas[ns]

  cpu_limits := [parse_cpu(c.resources.limits.cpu) | c := input.review.object.spec.containers[_]]
  total_cpu := sum(cpu_limits)

  limit_val := parse_cpu(ns_quota.cpu)
  total_cpu > limit_val

  msg := sprintf("CPU quota exceeded for namespace '%s': %.2f > %.2f", [ns, total_cpu, limit_val])
}
