#!/usr/bin/env bun
/**
 * archive_legacy.ts — V25 Pinnacle Legacy Script Archival
 *
 * Scans for legacy Bash/Python scripts that have been superseded by
 * Bun-native TypeScript equivalents and moves them to .archive/legacy/
 * with a manifest recording the migration timestamp and replacement file.
 *
 * Usage: bun run scripts/archive_legacy.ts [--dry-run] [--verbose]
 */
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "fs";
import { basename, extname, join } from "path";

const WORKSPACE =
  process.env.WORKSPACE_ROOT || "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball";
const ARCHIVE_DIR = join(WORKSPACE, ".archive", "legacy");
const MANIFEST_PATH = join(ARCHIVE_DIR, "archive_manifest.json");

const DRY_RUN = process.argv.includes("--dry-run");
const VERBOSE = process.argv.includes("--verbose");

/** Known legacy → replacement mappings */
const MIGRATION_MAP: Record<string, string> = {
  "scripts/auth_github_app.py": "scripts/auth_github_app.ts",
  "scripts/repo_doctor.py": "scripts/repo_doctor.ts",
  "scripts/omega_sync_legacy.sh": "scripts/omega_sync.ts",
  "scripts/provision_data_plane.sh": "scripts/provision_data_plane.ts",
  "scripts/setup_wif.sh": "scripts/setup_wif.ts",
  "scripts/port_killer.sh": "scripts/port_killer.ts",
  "scripts/ast_surgery.sh": "scripts/ast_surgery.ts",
};

interface ArchiveEntry {
  originalPath: string;
  replacedBy: string;
  archivedAt: string;
  archivePath: string;
}

function loadManifest(): ArchiveEntry[] {
  if (existsSync(MANIFEST_PATH)) {
    return JSON.parse(readFileSync(MANIFEST_PATH, "utf-8"));
  }
  return [];
}

function saveManifest(entries: ArchiveEntry[]): void {
  writeFileSync(MANIFEST_PATH, JSON.stringify(entries, null, 2));
}

function archiveFile(legacyPath: string, replacedBy: string, manifest: ArchiveEntry[]): boolean {
  const fullLegacy = join(WORKSPACE, legacyPath);
  const fullReplacement = join(WORKSPACE, replacedBy);

  if (!existsSync(fullLegacy)) {
    if (VERBOSE) console.log(`  SKIP: ${legacyPath} (not found)`);
    return false;
  }

  if (!existsSync(fullReplacement)) {
    console.warn(`  WARN: replacement ${replacedBy} missing — skipping ${legacyPath}`);
    return false;
  }

  const ext = extname(legacyPath);
  const base = basename(legacyPath, ext);
  const archiveName = `${base}_${Date.now()}${ext}`;
  const archivePath = join(ARCHIVE_DIR, archiveName);

  if (DRY_RUN) {
    console.log(`  DRY-RUN: ${legacyPath} → .archive/legacy/${archiveName}`);
    return true;
  }

  renameSync(fullLegacy, archivePath);

  manifest.push({
    originalPath: legacyPath,
    replacedBy,
    archivedAt: new Date().toISOString(),
    archivePath: `.archive/legacy/${archiveName}`,
  });

  console.log(`  ARCHIVED: ${legacyPath} → .archive/legacy/${archiveName}`);
  return true;
}

// Main
console.log(`\n🗄️  Legacy Script Archival (V25 Pinnacle)`);
console.log(`   Workspace: ${WORKSPACE}`);
console.log(`   Mode: ${DRY_RUN ? "DRY-RUN" : "LIVE"}\n`);

if (!existsSync(ARCHIVE_DIR)) {
  mkdirSync(ARCHIVE_DIR, { recursive: true });
}

const manifest = loadManifest();
let archived = 0;

for (const [legacy, replacement] of Object.entries(MIGRATION_MAP)) {
  if (archiveFile(legacy, replacement, manifest)) {
    archived++;
  }
}

if (!DRY_RUN && archived > 0) {
  saveManifest(manifest);
}

console.log(`\n✅ ${archived} file(s) ${DRY_RUN ? "would be" : ""} archived.`);
if (manifest.length > 0) {
  console.log(`   Total in manifest: ${manifest.length}`);
}
