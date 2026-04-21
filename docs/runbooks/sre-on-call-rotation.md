# SRE On-Call Rotation

## Current Team
| Name | Role | Contact | Timezone |
|------|------|---------|----------|
| Founder (Erik) | Primary | founder@shadowtagai.com | US Pacific |

## Rotation Schedule
- **Phase 1 (Current)**: Founder is sole on-call
- **Phase 2 (Post-hire)**: Weekly rotation, 2-person team minimum
- **Phase 3 (Scale)**: Follow-the-sun with 3 timezone coverage

## Escalation Matrix
| Severity | Response SLA | Escalation |
|----------|-------------|------------|
| P1 (Service Down) | 15 min | Immediate page, all hands |
| P2 (Degraded) | 1 hour | Email + FCM push |
| P3 (Non-urgent) | 4 hours | Email notification |
| P4 (Enhancement) | Next business day | Async |

## Alerting Channels
1. **Email**: founder@shadowtagai.com (PagerDuty integration)
2. **FCM Push**: admin-alerts topic
3. **Cloud Monitoring**: 14 alert policies active

## Incident Workflow
1. **Acknowledge** alert within SLA
2. **Assess** severity using dashboards:
   - CounselConduit Operations dashboard
   - Error Budget SLO Dashboard
3. **Mitigate** using runbooks:
   - Circuit breaker → `docs/runbooks/circuit-breaker-incident.md`
   - Canary rollback → `docs/runbooks/canary-traffic-split.md`
   - Data loss → `docs/runbooks/firestore-backup-restore.md`
   - Failover → `docs/runbooks/multi-region-failover.md`
4. **Communicate** status to stakeholders
5. **Post-mortem** within 48 hours for P1/P2

## Health Checks
- 8 uptime checks (5 min intervals)
- Cloud Scheduler heartbeats (session-pin-cleanup, daily backup)
- SLO target: 99.5% availability (30-day window)

## Handoff Procedure
1. Review open incidents and on-going investigations
2. Check error budget consumption
3. Verify all runbooks are accessible
4. Confirm alerting channels are routing correctly
5. Test page/notification delivery
