package mutation_hpa

mutation {
  input.request.kind.kind == "HorizontalPodAutoscaler"
  patch := {
    "spec": {
      "minReplicas": 3,
      "metrics": [{
        "type": "Resource",
        "resource": {"name": "cpu", "target": {"type": "Utilization", "averageUtilization": 70}}
      }]
    }
  }
  mutation.reviewResponse = {
    "allowed": true,
    "patchType": "JSONPatch",
    "patch": [json.patch(patch, input.request.object)]
  }
}
