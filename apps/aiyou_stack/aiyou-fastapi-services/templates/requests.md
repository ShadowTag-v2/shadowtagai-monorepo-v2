# SPECIFIC REQUEST TEMPLATES (Habit 9)

## Resource Updates
"Update judge namespace resource quota: CPU 100 → 200 cores in kubernetes/quotas.yaml:45"

## Annotation Fixes
"Fix istio sidecar injection annotation in judge-layer1-deployment.yaml:23"

## Scaling Changes
"Change GPU count from 1 to 2 in terraform/node-pools.tf:156 for layer2 pool"

## Threshold Adjustments
"Adjust p99 alert threshold from 90ms to 85ms in monitoring/alerts.yaml:89"

## HPA Tuning
"Set judge-layer1 HPA min replicas to 2 for HA in kubernetes/judge/layer1/hpa.yaml:12"
