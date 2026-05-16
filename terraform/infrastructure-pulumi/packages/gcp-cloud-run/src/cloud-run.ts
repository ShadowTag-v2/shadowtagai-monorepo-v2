import * as gcp from "@pulumi/gcp";
import * as pulumi from "@pulumi/pulumi";

export interface CloudRunArgs {
  name: string;
  projectId: string;
  region: string;
  image: string;
  // Gen2 performance
  startupCpuBoost?: boolean;
  minInstances?: number;
  maxInstances?: number;
  concurrency?: number;
  cpu?: string;
  memory?: string;
  // Networking
  vpcConnectorId?: pulumi.Input<string>;
  vpcEgress?: "ALL_TRAFFIC" | "PRIVATE_RANGES_ONLY";
  // Cloud SQL
  cloudSqlInstances?: string[];
  // Secrets (rotation-safe: default version = "latest")
  envVars?: Record<string, string>;
  secrets?: Array<{ secretId: string; version?: string; envVarName: string }>;
  // Traffic / canary
  traffic?: Array<{ percent: number; latestRevision?: boolean; revision?: string }>;
  // IAM
  allowUnauthenticated?: boolean;
  serviceAccountEmail?: string;
  // Observability
  environment?: string;
  team?: string;
  enableOtel?: boolean;
  deletionProtection?: boolean;
}

export class CloudRun extends pulumi.ComponentResource {
  public readonly service: gcp.cloudrunv2.Service;
  public readonly url: pulumi.Output<string>;
  public readonly revisionName: pulumi.Output<string>;
  public readonly monitoringUrl: pulumi.Output<string>;
  public readonly traceUrl: pulumi.Output<string>;

  constructor(name: string, args: CloudRunArgs, opts?: pulumi.ComponentResourceOptions) {
    super("antigravity:gcp:CloudRun", name, args, opts);

    const cfg = {
      startupCpuBoost: true,
      minInstances: 1,
      maxInstances: 10,
      concurrency: 80,
      cpu: "1",
      memory: "512Mi",
      vpcEgress: "PRIVATE_RANGES_ONLY" as const,
      allowUnauthenticated: false,
      deletionProtection: true,
      environment: "prod",
      team: "backend",
      enableOtel: true,
      traffic: [{ percent: 100, latestRevision: true }],
      ...args,
    };

    const otelEnv = cfg.enableOtel
      ? { OTEL_SERVICE_NAME: args.name, OTEL_TRACES_SAMPLER: "always_on" }
      : {};

    const allEnvs = Object.entries({ ...cfg.envVars, ...otelEnv }).map(([n, v]) => ({
      name: n,
      value: v,
    }));

    const secretEnvs = (cfg.secrets ?? []).map((s) => ({
      name: s.envVarName,
      valueSource: { secretKeyRef: { secret: s.secretId, version: s.version ?? "latest" } },
    }));

    const sqlVolumes = (cfg.cloudSqlInstances ?? []).map((inst, i) => ({
      name: `cloudsql-${i}`,
      cloudSqlInstance: { instances: [inst] },
    }));

    const sqlMounts = sqlVolumes.map((v) => ({
      name: v.name,
      mountPath: "/cloudsql",
    }));

    this.service = new gcp.cloudrunv2.Service(
      name,
      {
        name: args.name,
        location: args.region,
        project: args.projectId,
        deletionProtection: cfg.deletionProtection,
        ingress: "INGRESS_TRAFFIC_ALL",
        labels: { environment: cfg.environment, team: cfg.team, managed_by: "pulumi" },
        template: {
          executionEnvironment: "EXECUTION_ENVIRONMENT_GEN2",
          serviceAccount: args.serviceAccountEmail,
          startupCpuBoost: cfg.startupCpuBoost,
          scaling: { minInstanceCount: cfg.minInstances, maxInstanceCount: cfg.maxInstances },
          containers: [
            {
              image: args.image,
              resources: { limits: { cpu: cfg.cpu, memory: cfg.memory } },
              ports: [{ containerPort: 8080 }],
              envs: [...allEnvs, ...secretEnvs],
              volumeMounts: sqlMounts,
              startupProbe: {
                httpGet: { path: "/healthz" },
                initialDelaySeconds: 10,
                periodSeconds: 30,
              },
              livenessProbe: {
                httpGet: { path: "/healthz" },
                initialDelaySeconds: 30,
                periodSeconds: 30,
              },
            },
          ],
          volumes: sqlVolumes,
          vpcAccess: args.vpcConnectorId
            ? { connector: args.vpcConnectorId, egress: cfg.vpcEgress }
            : undefined,
        },
        traffics: cfg.traffic.map((t) => ({
          percent: t.percent,
          latestRevision: t.latestRevision,
          revision: t.revision,
        })),
      },
      { parent: this },
    );

    if (cfg.allowUnauthenticated) {
      new gcp.cloudrunv2.ServiceIamMember(
        "invoker",
        {
          project: args.projectId,
          location: args.region,
          name: this.service.name,
          role: "roles/run.invoker",
          member: "allUsers",
        },
        { parent: this },
      );
    }

    if ((cfg.cloudSqlInstances ?? []).length > 0 && args.serviceAccountEmail) {
      new gcp.projects.IAMMember(
        "cloudsql-client",
        {
          project: args.projectId,
          role: "roles/cloudsql.client",
          member: pulumi.interpolate`serviceAccount:${args.serviceAccountEmail}`,
        },
        { parent: this },
      );
    }

    // Observability: error rate alert
    new gcp.monitoring.AlertPolicy(
      "error-rate",
      {
        displayName: `${args.name} — High Error Rate`,
        combiner: "OR",
        conditions: [
          {
            displayName: "5xx rate > 5%",
            conditionThreshold: {
              filter: `resource.type="cloud_run_revision" AND resource.labels.service_name="${args.name}" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"`,
              aggregations: [{ alignmentPeriod: "300s", perSeriesAligner: "ALIGN_RATE" }],
              comparison: "COMPARISON_GT",
              thresholdValue: 0.05,
              duration: "300s",
              trigger: { count: 1 },
            },
          },
        ],
        notificationChannels: [],
      },
      { parent: this },
    );

    this.url = this.service.uri;
    this.revisionName = this.service.template.apply((t) => t.revision ?? "unknown");
    this.monitoringUrl = pulumi.interpolate`https://console.cloud.google.com/monitoring?project=${args.projectId}`;
    this.traceUrl = pulumi.interpolate`https://console.cloud.google.com/traces?project=${args.projectId}`;

    this.registerOutputs({ url: this.url, revision: this.revisionName });
  }
}
