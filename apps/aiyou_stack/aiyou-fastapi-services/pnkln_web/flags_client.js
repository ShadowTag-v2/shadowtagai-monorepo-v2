let cache = {};
export async function refreshFlags() {
  const r = await fetch("/config/feature_flags.yaml", { cache: "no-store" });
  const t = await r.text();
  // minimal YAML parse for flags: assumes simple key: bool entries
  const lines = t.split("\n");
  const flags = {};
  let inFlags = false;
  for (const line of lines) {
    if (line.trim() === "flags:") {
      inFlags = true;
      continue;
    }
    if (inFlags && line.includes(":")) {
      const [k, v] = line
        .trim()
        .split(":")
        .map((s) => s.trim());
      flags[k] = v === "true";
    }
  }
  cache = flags;
}
export const isEnabled = (k) => !!cache[k];
