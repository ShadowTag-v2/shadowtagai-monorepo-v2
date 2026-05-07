# ROBUST_MEATWARE_EVICTION_PROMPT.md

**Version**: 2.0 (Enhanced Error Handling + Resilience)  
**Date**: May 6, 2026

---

## Master Prompt (Copy-Paste Ready)

```
You are Antigravity executing the "Meatware Bridge Eviction v2.0" protocol with full autonomous control and advanced error recovery.

I am the asynchronous reviewer. You now have complete ownership of the generative asset pipeline using your Native Browser Subagent and chrome-devtools-mcp.

**MANDATE**: Execute the full pipeline below without any human intervention. Use visual feedback loops, retry logic, and fallback strategies to handle failures gracefully. Do not stop or ask for help.

---

### PHASE 1: Autonomous Image Generation (ImageFX)

**Target URL**: https://aitestkitchen.withgoogle.com/tools/image-fx

**Steps**:
1. Navigate to the target URL.
2. Read the "Primary (Gavel Impact)" prompt from: external_payloads/PROMPT_SPECS.md
3. Attempt to locate the prompt input field using standard selectors.
4. If selectors fail (common due to Shadow DOM/Canvas), immediately:
   - Take a full-page screenshot
   - Analyze the screenshot visually
   - Use coordinate-based clicking (X/Y via evaluate_script) to focus the input area
5. Paste the full "Gavel Impact" prompt.
6. Click the Generate button (use visual detection if needed).
7. Implement a **visual polling loop**:
   - Take a screenshot every 15 seconds
   - Check for completion indicators (download button, progress bar disappearance, or image preview)
   - Maximum wait time: 4 minutes
8. Once the image is ready, download it.
9. Move and rename the file to: `apps/kovelai/public/frames/frame_0000.png`

**Error Handling**:
- If generation fails twice → Take screenshot + log error + try alternative URL if available
- If download fails → Use terminal to check ~/Downloads folder and move the most recent image

---

### PHASE 2: Autonomous Video Generation (VideoFX)

**Target URL**: https://aitestkitchen.withgoogle.com/tools/video-fx

**Steps**:
1. Navigate to the target URL.
2. Locate and click the image upload button.
3. Upload `frame_0000.png` as the reference image.
4. Read the "Primary (Gavel Descent)" prompt from: external_payloads/PROMPT_SPECS.md
5. Inject the full video prompt into the text field.
6. Click Generate.
7. Implement a **visual polling loop**:
   - Take a screenshot every 30 seconds
   - Check for download button or completion state
   - Maximum wait time: 8 minutes
8. Once ready, download the .mp4 file.
9. Move the file to: `labs/uphillsnowball/external_payloads/veo_output/hero_gavel.mp4`

**Error Handling**:
- If upload fails → Retry with coordinate clicking
- If generation times out → Log error + proceed with image-only assets (graceful degradation)

---

### PHASE 3: Pipeline Egress & Code Synchronization

**Steps**:
1. Run the extraction script:
   ```
   ./scripts/extract_frames.sh labs/uphillsnowball/external_payloads/veo_output/hero_gavel.mp4 apps/kovelai/public/frames 30
   ```
2. Count the exact number of extracted frames:
   ```
   ls -1 apps/kovelai/public/frames | wc -l
   ```
3. Update the `FRAME_COUNT` constant in both:
   - `chassis-preview.html`
   - `GavelHero.tsx`
4. Commit all changes using your `omega-sync` workflow.

---

### FINAL RULES & SAFEGUARDS

- Never pause for human input.
- Always prefer visual feedback (screenshots + DOM inspection) over brittle selectors.
- If any step fails after 3 attempts, log the error clearly and proceed with best-effort results.
- At the very end, output **exactly** this sentence with no additional text:

"Meatware Bridge evicted v2.0. Assets autonomously generated with error recovery, extracted, and codebase synchronized."

Execute the full pipeline now.
```

---

**End of ROBUST_MEATWARE_EVICTION_PROMPT.md**