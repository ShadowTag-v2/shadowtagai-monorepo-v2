# Hybrid RBAC + ABAC Rego
package hybrid_guard

import future.keywords.in

# Combine Role-Based and Attribute-Based Checks
allow {
    rbac_role(input.user)
    abac_risk(input) < 50
    not eval_danger(input.payload)
    not is_restricted_namespace(input.request.namespace)
}

rbac_role(user) {
    roles := {"hht_leader", "trusted_monkey", "trusted_troop"}
    user.roles[_] in roles
}

abac_risk(input) = score {
    score := input.risk_score
}

eval_danger(payload) {
    "eval(" in payload
}

eval_danger(payload) {
    "exec(" in payload
}

is_restricted_namespace(ns) {
    ns == "kube-system"
}

# Penal isolation: Deny external swarm on anomaly
is_restricted_namespace(ns) {
    ns == "penal-colony"
    input.user.role != "trusted_troop"
}
