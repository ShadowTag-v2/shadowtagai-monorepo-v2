import { CloudRun } from "@shadowtag/gcp-cloud-run";

const api = new CloudRun("api-v1", {
  name: "api",
  projectId: "shadowtag-omega-v4",
  region: "us-central1",
  image: "us-central1-docker.pkg.dev/shadowtag-omega-v4/api:latest",
});

export const url = api.url;
