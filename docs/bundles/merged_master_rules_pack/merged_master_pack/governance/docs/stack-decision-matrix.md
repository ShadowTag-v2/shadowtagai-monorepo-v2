# Stack Decision Matrix

## Auth

Default: managed auth provider
Switch when: compliance, pricing, or customization requires it
Trap: building auth yourself

## Database

Default: managed Postgres with a strong authorization model
Switch when: sync, edge, or product constraints justify it
Trap: choosing by hype instead of access model and ops burden

## Vector store

Default: simplest option that meets recall and latency needs
Switch when: scale, filtering, hybrid retrieval, or ops cost demand it
Trap: premature specialization

## Hosting

Default: platform that best fits your runtime and team shape
Switch when: pricing, egress, jobs, or region support force it
Trap: cargo-culting frontend hosting for backend-heavy systems

## Backend

Default: framework that fits your workload and team
Switch when: latency, hiring, ecosystem, or inference workflow changes
Trap: ideology over throughput

## Mobile

Default: fastest path that still meets requirements
Switch when: native-only capabilities force it
Trap: forcing native complexity too early
