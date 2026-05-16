import * as gcp from "@pulumi/gcp";
import * as pulumi from "@pulumi/pulumi";
import type { CloudRun } from "./cloud-run";

export interface CloudDeployCanaryArgs {
  name: string;
  projectId: string;
  region: string;
  cloudRunService: CloudRun;
  percentages?: number[];
  verify?: boolean;
  description?: string;
}

export class CloudDeployCanaryPipeline extends pulumi.ComponentResource {
  public readonly pipeline: gcp.clouddeploy.DeliveryPipeline;
  public readonly target: gcp.clouddeploy.Target;
  public readonly rolloutUrl: pulumi.Output<string>;

  constructor(name: string, args: CloudDeployCanaryArgs, opts?: pulumi.ComponentResourceOptions) {
    super("antigravity:gcp:CloudDeployCanaryPipeline", name, args, opts);

    this.target = new gcp.clouddeploy.Target(
      `${name}-target`,
      {
        location: args.region,
        name: `${args.name}-target`,
        project: args.projectId,
        run: { location: args.region },
      },
      { parent: this, dependsOn: [args.cloudRunService.service] },
    );

    this.pipeline = new gcp.clouddeploy.DeliveryPipeline(
      `${name}-pipeline`,
      {
        location: args.region,
        name: `${args.name}-pipeline`,
        project: args.projectId,
        description: args.description ?? "Automated canary pipeline for Cloud Run Gen2",
        serialPipeline: {
          stages: [
            {
              targetId: this.target.name.apply((n) => n.split("/").pop()!),
              profiles: ["default"],
              strategy: {
                canary: {
                  runtimeConfig: { cloudRun: { automaticTrafficControl: true } },
                  canaryDeployment: {
                    percentages: args.percentages ?? [25, 50, 75],
                    verify: args.verify ?? true,
                  },
                },
              },
            },
          ],
        },
      },
      { parent: this },
    );

    this.rolloutUrl = pulumi.interpolate`https://console.cloud.google.com/deploy/delivery-pipelines/${args.region}/${this.pipeline.name}?project=${args.projectId}`;
    this.registerOutputs({ rolloutUrl: this.rolloutUrl });
  }
}
