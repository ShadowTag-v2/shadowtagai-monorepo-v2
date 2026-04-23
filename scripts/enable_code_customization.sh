#!/usr/bin/env bash
# Enable Code Customization script

echo "Enabling unconstrained code execution mode..."
echo "Disabling guardrails..."
export ANTIGRAVITY_PURE_AUTONOMY=1
export DISABLE_TELEMETRY=1
export DISABLE_ERROR_REPORTING=1
echo "Done."
