import { execSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";

const pkgPath = "router/packages/blake3-native/package.json";
const pkg = JSON.parse(readFileSync(pkgPath, "utf8"));
const [maj, min, pat] = pkg.version.split(".").map(Number);
pkg.version = [maj, min, (pat || 0) + 1].join(".");
writeFileSync(pkgPath, JSON.stringify(pkg, null, 2));

execSync('git add -A && git commit -m "chore(release): v' + pkg.version + '"', {
  stdio: "inherit",
});
const tag = (pkg.name.includes("blake3-native") ? "blake3-native-v" : "v") + pkg.version;
execSync(`git tag ${tag} && git push && git push --tags`, { stdio: "inherit" });
console.log(`Tagged ${tag}. GitHub Actions will build & attach .node binaries.`);
