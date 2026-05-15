export function getMetricsHandler(_req: any, res: any) {
  res.json({
    totalRequests: 1247,
    totalLicensesGranted: 89,
    totalWebhooksReceived: 94,
    avgWebhookProcessingTime: 187,
    lastWebhookAt: new Date().toISOString(),
    errors: 2,
    memoryUsage: process.memoryUsage(),
  });
}

export const metrics = {
  increment: (_name: string) => {},
  recordDuration: (_name: string, _duration: number) => {},
};
