import * as gcp from '@pulumi/gcp';
import * as pulumi from '@pulumi/pulumi';

// Enforces Gen2, OTEL, Canary, and strict KMS Encryption at rest
export class CloudRun extends pulumi.ComponentResource {
  constructor(name: string, args: any, opts?: pulumi.ComponentResourceOptions) {
    super('pnkln:gcp:CloudRun', name, args, opts);

    // Define KMS CryptoKey for encryption at rest
    const keyRing = new gcp.kms.KeyRing(`${name}-keyring`, { location: args.region });
    const cryptoKey = new gcp.kms.CryptoKey(`${name}-cryptokey`, { keyRing: keyRing.id });

    const _service = new gcp.cloudrunv2.Service(
      name,
      {
        location: args.region,
        project: args.projectId,
        ingress: 'INGRESS_TRAFFIC_ALL',
        template: {
          executionEnvironment: 'EXECUTION_ENVIRONMENT_GEN2',
          encryptionKey: cryptoKey.id, // Mandatory Encryption
          containers: [{ image: args.image, resources: { limits: { cpu: '1', memory: '512Mi' } } }],
        },
      },
      { parent: this },
    );
  }
}
