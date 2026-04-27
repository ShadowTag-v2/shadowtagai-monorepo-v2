import * as gcp from '@pulumi/gcp';

interface UptimeCheckArgs {
  host: string;
  path?: string;
  period?: string;
  timeout?: string;
}

export function createUptimeCheck(name: string, args: UptimeCheckArgs) {
  return new gcp.monitoring.UptimeCheckConfig(`${name}-uptime`, {
    displayName: `${name}-health`,
    timeout: args.timeout ?? '10s',
    period: args.period ?? '60s',
    httpCheck: {
      port: 443,
      useSsl: true,
      path: args.path ?? '/health',
      validateSsl: true,
    },
    monitoredResource: {
      type: 'uptime_url',
      labels: { host: args.host },
    },
  });
}

interface AlertPolicyArgs {
  adminEmail: string;
  firestoreWriteThreshold?: number;
}

export function createAlertPolicy(name: string, args: AlertPolicyArgs) {
  const channel = new gcp.monitoring.NotificationChannel(`${name}-email`, {
    displayName: `${name} Admin Alerts`,
    type: 'email',
    labels: { email_address: args.adminEmail },
  });

  new gcp.monitoring.AlertPolicy(`${name}-firestore-spike`, {
    displayName: `${name} — High Firestore Usage`,
    combiner: 'OR',
    conditions: [
      {
        displayName: 'Firestore Write Spikes',
        conditionThreshold: {
          filter:
            'metric.type="firestore.googleapis.com/document/write_count" AND resource.type="firestore_database"',
          comparison: 'COMPARISON_GT',
          thresholdValue: args.firestoreWriteThreshold ?? 50000,
          duration: '300s',
          aggregations: [
            {
              alignmentPeriod: '60s',
              perSeriesAligner: 'ALIGN_RATE',
            },
          ],
        },
      },
    ],
    notificationChannels: [channel.name],
  });

  return channel;
}
