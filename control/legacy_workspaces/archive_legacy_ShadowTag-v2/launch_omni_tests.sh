#!/bin/bash
echo "Initiating 4-Phase Omni-Cortex Verification sequence..." > /tmp/omni_cortex_test.log

echo "Command 1: Infinite Planning Test" >> /tmp/omni_cortex_test.log
gemini -s -y -p '/pickle-prd "@[planning-with-files] Architect a highly-scalable, real-time analytics dashboard for ShadowTag'\''s user dashboard. It must track agent token usage, task success rates, and API failures across multiple local projects. Write the complete master plan, progress structure, and findings to the filesystem. Do not write any implementation code yet. Terminate execution and await my authorization."' >> /tmp/omni_cortex_test.log 2>&1

echo "Command 2: Corporate Artifact Generation (PPTX)" >> /tmp/omni_cortex_test.log
gemini -s -y -p '/pickle "@[pptx] Generate a 5-slide pitch deck for ShadowTag AI. Slide 1: Title and Vision. Slide 2: The Problem with naive AI coding. Slide 3: Our Solution: The Antigravity Swarm Architecture. Slide 4: Real-world metrics and ROI. Slide 5: Call to Action. Use your best styling options. Save the presentation as shadowtag_pitch.pptx in the root directory and commit it locally."' >> /tmp/omni_cortex_test.log 2>&1

echo "Command 3: Systematic Debugging" >> /tmp/omni_cortex_test.log
gemini -s -y -p '/pickle "@[systematic-debugging] Our frontend server on localhost:3000 is throwing a React hydration mismatch error on the main landing page. Use the chrome-devtools MCP to load the page, analyze the DOM and console logs, form a hypothesis, and systematically fix the codebase. Verify the fix clears the error in the browser before using git commit."' >> /tmp/omni_cortex_test.log 2>&1

echo "Command 4: Boot Knowledge API Hook" >> /tmp/omni_cortex_test.log
python3 scripts/hook_knowledge_api.py >> /tmp/omni_cortex_test.log 2>&1

echo "Omni-Cortex Tests 1-4 Complete." >> /tmp/omni_cortex_test.log
