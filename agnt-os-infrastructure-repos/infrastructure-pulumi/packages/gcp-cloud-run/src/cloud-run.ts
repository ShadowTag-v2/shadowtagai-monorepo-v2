import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

export class CloudRun extends pulumi.ComponentResource {
  public readonly url: pulumi.Output<string>;

  constructor(name: string, args: any, opts?: pulumi.ComponentResourceOptions) {
    super("shadowtag:gcp:CloudRun", name, args, opts);

    const service = new gcp.cloudrunv2.Service(name, {
      name: args.name,
      location: args.region,
      project: args.projectId,
      template: {
        executionEnvironment: "EXECUTION_ENVIRONMENT_GEN2",
        startupCpuBoost: true,
        containers: [{
          image: args.image,
          resources: { limits: { cpu: "1", memory: "512Mi" } },
          startupProbe: { httpGet: { path: "/healthz" }, initialDelaySeconds: 10 },
        }],
      },
      traffic: args.traffic || [{ percent: 100, latestRevision: true }],
    });

    this.url = service.uri;
    this.registerOutputs({ url: this.url });
  }
}
