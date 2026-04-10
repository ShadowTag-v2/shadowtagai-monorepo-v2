import fs from "node:fs";
const paths = ["dist/linux-x64","dist/win-x64","dist/macos-x64","dist/macos-arm64"];
const missing = paths.filter(p=>!fs.existsSync(p));
if (missing.length) {
  console.warn("Missing build targets:", missing.join(", "));
  process.exitCode = 0; // warn only
} else {
  console.log("All native targets present.");
}

