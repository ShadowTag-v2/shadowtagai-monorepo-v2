import { createCloudRunService } from "./cloud-run";
import { createUptimeCheck, createAlertPolicy } from "./monitoring";

// ── CounselConduit ──
const counselconduit = createCloudRunService("counselconduit", {
  image: "us-central1-docker.pkg.dev/shadowtag-omega-v4/counselconduit/api:latest",
  minInstances: 1,
  maxInstances: 10,
  concurrency: 100,
  serviceAccount: "counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com",
  env: {
    APP_ENV: "production",
    CLOUD_RUN_URL: "https://counselconduit-767252945109.us-central1.run.app",
  },
  traceSampleRate: "0.1",
});

createUptimeCheck("counselconduit", {
  host: "counselconduit-767252945109.us-central1.run.app",
});

createAlertPolicy("counselconduit", {
  adminEmail: "admin@shadowtagai.com",
  firestoreWriteThreshold: 50000,
});

// ── Exports ──
export const counselconduitUrl = counselconduit.uri;
