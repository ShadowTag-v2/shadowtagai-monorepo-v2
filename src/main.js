const os = require("node:os");
const path = require("node:path");
const { app } = require("electron");

// Force gcloud into the environment natively
const gcloudPath = path.join(os.homedir(), "google-cloud-sdk", "bin");
if (!process.env.PATH?.includes(gcloudPath)) {
  process.env.PATH = `${gcloudPath}${path.delimiter}${process.env.PATH || ""}`;
}

// Bypass unsigned macOS Keychain restrictions for persistent Cloud Code auth
app.commandLine.appendSwitch("password-store", "basic");
