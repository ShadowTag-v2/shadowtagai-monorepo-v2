package penal_colony.monkeys7
default allow := false

# CSRMC-2025 Compliance: Trusted Troop Access
allow {
  input.user.role == "trusted_troop"
  input.risk_score < 50
  input.location == "secure_zone"
}

# Deny if active breach protocol (R-Kill)
deny {
  data.breach_protocol.active == true
}
