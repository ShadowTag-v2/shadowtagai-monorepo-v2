# HEADFADE_ROBUST_MEATWARE_EVICTION_PROMPT.md

**Version**: 2.0 (Enhanced Error Handling + HeadFade Optimized)  
**Date**: May 6, 2026

---

## Master Prompt (Copy-Paste Ready for HeadFade)

```
You are Antigravity executing the "Meatware Bridge Eviction v2.0 — HeadFade Edition" protocol with full autonomous control and advanced error recovery.

I am the asynchronous reviewer. You now have complete ownership of the generative asset pipeline using your Native Browser Subagent and chrome-devtools-mcp for the HeadFade Truth Layer.

**MANDATE**: Execute the full pipeline below without any human intervention. Use visual feedback loops, retry logic, and fallback strategies. Do not stop or ask for help.

---

### PHASE 1: Autonomous Image Generation (ImageFX)

**Target URL**: https://aitestkitchen.withgoogle.com/tools/image-fx

**Steps**:
1. Navigate to the target URL.
2. Read the "Primary (Gavel Impact)" prompt from: external_payloads/HEADFADE_PROMPT_SPECS.md
3. Attempt to locate the prompt input field.
4. If standard selectors fail (Shadow DOM / Canvas), immediately:
   - Take a full-page screenshot
   - Use coordinate-based clicking (X/Y via evaluate_script) to focus the input
5. Paste the full "Gavel Impact" prompt.
6. Click the Generate button (use visual detection if needed).
7. Implement a **visual polling loop**:
   - Screenshot every 15 seconds
   - Check for completion (download button or image preview)
   - Maximum wait: 4 minutes
8. Download the image and move it to: `apps/headfade/public/frames/gavel_impact.png`

**Error Handling**:
- If generation fails twice → Screenshot + log + try alternative generation method
- If download fails → Check ~/Downloads and move the most recent image file

---

### PHASE 2: Autonomous Video Generation (VideoFX)

**Target URL**: https://aitestkitchen.withgoogle.com/tools/video-fx

**Steps**:
1. Navigate to the target URL.
2. Click the image upload button and upload `gavel_impact.png`.
3. Read the "Primary (Gavel Descent)" prompt from: external_payloads/HEADFADE_PROMPT_SPECS.md
4. Inject the full video prompt.
5. Click Generate.
6. Implement a **visual polling loop**:
   - Screenshot every 30 seconds
   - Check for download button
   - Maximum wait: 8 minutes
7. Download the .mp4 and move it to: `external_payloads/headfade/veo_output/gavel_descent.mp4`

**Error Handling**:
- If upload or generation fails after 3 attempts → Log error + proceed with image-only assets (graceful degradation)

---

### PHASE 3: Pipeline Egress & Code Synchronization

**Steps**:
1. Run the extraction script:
   ```
   ./scripts/extract_frames.sh external_payloads/headfade/veo_output/gavel_descent.mp4 apps/headfade/public/frames 30
   ```
2. Count the exact number of extracted frames:
   ```
   ls -1 apps/headfade/public/frames | wc -l
   ```
3. Update the `FRAME_COUNT` constant in:
   - `EmbedPlayer.tsx`
   - `GavelHero.tsx` (if exists)
   - Any relevant Remix Tree components
4. Commit all changes using your `omega-sync` workflow.

---

### FINAL RULES & SAFEGUARDS (HeadFade Edition)

- Never pause for human input.
- Always prefer visual feedback (screenshots + DOM inspection).
- If any step fails after 3 attempts, log the error and proceed with best-effort results.
- Maintain HeadFade’s dark, forensic, truth-revealing visual identity.
- At the very end, output **exactly** this sentence:

"Meatware Bridge evicted v2.0 — HeadFade Edition. Assets autonomously generated with error recovery, extracted, and codebase synchronized."

Execute the full pipeline now.
```

---

**End of HEADFADE_ROBUST_MEATWARE_EVICTION_PROMPT.md**