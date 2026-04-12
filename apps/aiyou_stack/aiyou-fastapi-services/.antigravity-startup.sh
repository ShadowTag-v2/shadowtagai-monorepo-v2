#!/bin/bash
TARGET="/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2"
export PIP_USER=false
export PYTHONNOUSERSITE=1

# Nuke hallucinations (Targeting nested git/agent folders)
find "$TARGET" -mindepth 2 -type d -name ".git" -exec rm -rf {} +
find "$TARGET" -mindepth 2 -type d -name ".agent" -exec rm -rf {} +

# Re-assert rules
mkdir -p "$TARGET/.agent"
printf "- ROOT: %s\n- MODE: ANTIGRAVITY_FORCE\n- NO_NESTED_GIT\n" "$TARGET" > "$TARGET/.agent/rules.md"
