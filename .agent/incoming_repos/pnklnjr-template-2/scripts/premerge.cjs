#!/usr/bin/env node
const fs = require("fs");

const checks = [
  ["governance/pnklnjr.yml", "Missing pnklnJR governance file."],
  [".cursor/rules.md", "Missing Cursor Strict rules."],
  ["README.md", "Missing project README."],
];

let ok = true;
for (const [p, msg] of checks) {
  if (!fs.existsSync(p)) {
    console.error("❌", msg);
    ok = false;
  }
}
if (!ok) process.exit(2);
console.log("✅ Pre-merge governance present. Run unit tests & linters next.");
