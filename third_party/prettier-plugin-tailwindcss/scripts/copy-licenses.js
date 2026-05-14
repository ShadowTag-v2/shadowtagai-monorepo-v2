import * as fs from "node:fs/promises";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import checker from "license-checker";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const pkg = JSON.parse(await fs.readFile(path.resolve(__dirname, "../package.json"), "utf8"));

const exclude = ["vitest", "license-checker", "prettier", "svelte", "knip"];

/** @type {checker.ModuleInfo} */
const packages = await new Promise((resolve, reject) => {
  checker.init({ start: path.resolve(__dirname, "..") }, (_err, packages) => {
    if (_err) {
      reject(_err);
    } else {
      resolve(packages);
    }
  });
});

for (const key in packages) {
  const dep = packages[key];
  const name = key.split(/(?<=.)@/)[0];

  if (exclude.includes(name)) continue;
  if (!dep.licenseFile) continue;
  if (!(name in pkg.devDependencies)) continue;

  const dir = path.resolve(__dirname, "../dist/licenses", name);
  await fs.mkdir(dir, { recursive: true });
  await fs.copyFile(dep.licenseFile, path.resolve(dir, path.basename(dep.licenseFile)));
}
