import * as gcp from '@pulumi/gcp';
import * as pulumi from '@pulumi/pulumi';

interface CloudRunServiceArgs {
  image: string;
  minInstances?: number;
  maxInstances?: number;
  cpu?: string;
  memory?: string;
  concurrency?: number;
  env?: Record<string, string>;
  secretEnv?: Record<string, string>;
  serviceAccount?: string;
  healthCheckPath?: string;
  traceSampleRate?: string;
}

export function createCloudRunService(name: string, args: CloudRunServiceArgs) {
  const config = new pulumi.Config('gcp');
  const region = config.require('region');
  const stack = pulumi.getStack();

  const service = new gcp.cloudrunv2.Service(name, {
    location: region,
    ingress: 'INGRESS_TRAFFIC_ALL',
    template: {
      scaling: {
        minInstanceCount: args.minInstances ?? 0,
        maxInstanceCount: args.maxInstances ?? 10,
      },
      serviceAccount: args.serviceAccount,
      containers: [
        {
          image: args.image,
          resources: {
            limits: {
              cpu: args.cpu ?? '1000m',
              memory: args.memory ?? '512Mi',
            },
            startupCpuBoost: true,
          },
          envs: [
            ...Object.entries(args.env ?? {}).map(([k, v]) => ({
              name: k,
              value: v,
            })),
            {
              name: 'OTEL_EXPORTER_OTLP_ENDPOINT',
              value: 'https://monitoring.googleapis.com:443',
            },
            {
              name: 'OTEL_RESOURCE_ATTRIBUTES',
              value: `service.name=${name},deployment.environment=${stack}`,
            },
            {
              name: 'OTEL_TRACES_SAMPLER',
              value: 'parentbased_traceidratio',
            },
            {
              name: 'OTEL_TRACES_SAMPLER_ARG',
              value: args.traceSampleRate ?? '0.1',
            },
          ],
          startupProbe: {
            httpGet: { path: args.healthCheckPath ?? '/health' },
            initialDelaySeconds: 5,
            periodSeconds: 10,
            failureThreshold: 3,
          },
          livenessProbe: {
            httpGet: { path: args.healthCheckPath ?? '/health' },
            periodSeconds: 30,
          },
        },
      ],
      maxInstanceRequestConcurrency: args.concurrency ?? 100,
      executionEnvironment: 'EXECUTION_ENVIRONMENT_GEN2',
    },
    labels: {
      managed_by: 'pulumi',
      environment: stack,
      service: name,
    },
  });

  // Public access
  new gcp.cloudrunv2.ServiceIamMember(`${name}-public`, {
    project: service.project,
    location: service.location,
    name: service.name,
    role: 'roles/run.invoker',
    member: 'allUsers',
  });

  return service;
}
