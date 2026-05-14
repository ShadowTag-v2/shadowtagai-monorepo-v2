import * as gcp from "@pulumi/gcp";
import * as pulumi from "@pulumi/pulumi";

export interface VpcConnectorArgs {
  name: string;
  projectId: string;
  region: string;
  subnetName: string;
  machineType?: string;
  minInstances?: number;
  maxInstances?: number;
}

export class VpcConnector extends pulumi.ComponentResource {
  public readonly connector: gcp.vpcaccess.Connector;
  public readonly id: pulumi.Output<string>;
  public readonly name: pulumi.Output<string>;

  constructor(name: string, args: VpcConnectorArgs, opts?: pulumi.ComponentResourceOptions) {
    super("antigravity:gcp:VpcConnector", name, args, opts);

    this.connector = new gcp.vpcaccess.Connector(
      name,
      {
        name: args.name,
        region: args.region,
        project: args.projectId,
        machineType: args.machineType ?? "e2-micro",
        minInstances: args.minInstances ?? 2,
        maxInstances: args.maxInstances ?? 10,
        subnet: { name: args.subnetName },
      },
      { parent: this },
    );

    this.id = this.connector.id;
    this.name = this.connector.name;
    this.registerOutputs({ id: this.id, name: this.name });
  }
}
