---
name: 'Gideon OS Change'
about: Template for changes to Gideon OS architecture blocks
title: '[GIDEON-OS] '
labels: 'gideon-os, architecture'
assignees: ''
---

## Block Affected
<!-- Which of the 14 architecture blocks does this change affect? -->
- [ ] Vault Constitution
- [ ] KAIROS Supervisor
- [ ] Shield1 Ingress (Go)
- [ ] Zero-Trust Pipeline
- [ ] Pathway Ingest
- [ ] Midas Monte Carlo (C++/BigQuery)
- [ ] Panopticon
- [ ] Jurisdiction Forge
- [ ] Browser Extension
- [ ] Cor.Yay Bridge
- [ ] AdminLTE GlassBox
- [ ] Tauri Cockpit
- [ ] Sovereign Infra (Terraform)
- [ ] Genesis Bootstrapper

## Change Type
- [ ] Bug fix
- [ ] New feature
- [ ] Security hardening
- [ ] Compliance (Judge 6 / Federal)
- [ ] Infrastructure

## Description
<!-- What does this change do? -->

## Security Checklist (Cor.30)
- [ ] No secrets in code
- [ ] Inputs validated (Pydantic/Zod)
- [ ] Errors use RFC 9457 format
- [ ] No raw DB objects returned
- [ ] Rate limiting considered
- [ ] IPI quarantine maintained (Secure BLAST)

## Testing
- [ ] Unit tests added/updated
- [ ] `pytest` passes (499+)
- [ ] `.NET build` succeeds (if C# touched)
- [ ] `go vet` passes (if Go touched)
- [ ] `cargo check` passes (if Rust touched)
- [ ] Biome lint clean (if JS/TS touched)
