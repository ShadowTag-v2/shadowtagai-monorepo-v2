package rl_scheduling

rl_score := data.rl.scores[input.review.object.metadata.name]

deny[msg] {
  rl_score < 0.8
  msg := "RL score too low for scheduling"
}

allow if {
  node_taint := input.review.object.spec.nodeSelector["security"]
  node_taint == "penal-secure"
  rl_score > 0.8
}
