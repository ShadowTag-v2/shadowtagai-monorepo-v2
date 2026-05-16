// Given a version, figure out what the release notes are so that we can use this to pre-fill the
// relase notes on a GitHub release for the current version.

import * as fs from "node:fs/promises";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const pkg = JSON.parse(await fs.readFile(path.resolve(__dirname, "../package.json"), "utf8"));

const version = process.argv[2] || process.env.npm_package_version || pkg.version;

const changelog = await fs.readFile(path.resolve(__dirname, "..", "CHANGELOG.md"), "utf8");
const match = new RegExp(
  `## \\[${version}\\] - (.*)\\n\\n([\\s\\S]*?)\\n(?:(?:##\\s)|(?:\\[))`,
  "g",
).exec(changelog);

if (match) {
  const [, , notes] = match;
  console.log(notes.trim());
} else {
  console.log(`Placeholder release notes for version: v${version}`);
}
