# External Repos — Clone Yard

> **Manifest:** `upstream_manifest.yaml`

This directory hosts cloned external reference repositories used for architectural
benchmarking, skill acquisition, and CI/CD comparison. All repos in this directory
are **gitignored** — they are not committed to the monorepo.

## Structure

```
external_repos/
├── upstream_manifest.yaml   ← Canonical list of tracked repos
├── upstream/                ← Repos cloned by clone-external-reference-repos.sh
│   ├── tier0_core/          ← Critical infrastructure references
│   └── agent_protocols/     ← Agent framework references
├── ai-website-cloner/       ← Website cloning reference
└── numpy-100/               ← NumPy reference exercises
```

## Usage

```bash
# Clone all repos defined in the manifest
bash scripts/clone-external-reference-repos.sh

# Validate manifest structure (CI gate)
python3 -c "import yaml; yaml.safe_load(open('external_repos/upstream_manifest.yaml'))"
```

## Rules

1. **Never commit cloned repos** — `.gitignore` excludes `external_repos/*/`
2. **Manifest is committed** — `upstream_manifest.yaml` is the source of truth
3. **Clone on demand** — Repos are fetched when needed, not kept in sync
4. **DLP boundary** — No proprietary identifiers may cross from `external_repos/` into public code
