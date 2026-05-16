import { CloudDeployCanaryPipeline, CloudRun, VpcConnector } from "@antigravity/gcp-cloud-run";
import * as pulumi from "@pulumi/pulumi";

const cfg = new pulumi.Config();
const project = cfg.require("gcp:project");
const region = cfg.require("gcp:region");
const env = cfg.get("environment") ?? "dev";

const connector = new VpcConnector("private-run", {
  name: `private-run-${env}`,
  projectId: project,
  region,
  subnetName: "default",
});

const api = new CloudRun("lawtrack-api", {
  name: `lawtrack-api-${env}`,
  projectId: project,
  region,
  image: `us-central1-docker.pkg.dev/${project}/lawtrack/api:latest`,
  vpcConnectorId: connector.id,
  cloudSqlInstances: [`${project}:${region}:lawtrack-db-primary`],
  serviceAccountEmail: `lawtrack-api-sa@${project}.iam.gserviceaccount.com`,
  secrets: [{ secretId: "db-password", envVarName: "DB_PASS" }],
  envVars: { ENVIRONMENT: env },
  environment: env,
  team: "platform",
  minInstances: env === "prod" ? 2 : 0,
  // Canary example (uncomment for blue/green traffic split):
  // traffic: [
  //   { percent: 90, latestRevision: true },
  //   { percent: 10, revision: "lawtrack-api-dev-00042-abc" },
  // ],
});

const canary = new CloudDeployCanaryPipeline("lawtrack-api-canary", {
  name: `lawtrack-api-${env}`,
  projectId: project,
  region,
  cloudRunService: api,
  percentages: [25, 50, 75],
  verify: true,
});

export const serviceUrl = api.url;
export const monitoringUrl = api.monitoringUrl;
export const canaryRolloutUrl = canary.rolloutUrl;
