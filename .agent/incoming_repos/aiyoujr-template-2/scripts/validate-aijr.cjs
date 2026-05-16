#!/usr/bin/env node
const fs = require("fs");

function mustNum(label, val) {
  if (typeof val !== "number" || !isFinite(val)) throw new Error(`Invalid number for ${label}`);
}

try {
  const plan = JSON.parse(fs.readFileSync("plans/pnkln-stack.plan.json", "utf8"));
  mustNum("ARR_target", plan.metrics.ARR_target);
  mustNum("MAU_target", plan.metrics.MAU_target);
  if (!plan.brakes || !Array.isArray(plan.brakes) || plan.brakes.length === 0)
    throw new Error("Brakes missing (Army RM).");
  console.log("✅ pnkln-stackJR plan validates.");
} catch (e) {
  console.error("❌ pnkln-stackJR validation failed:", e.message);
  process.exit(2);
}
