# Playwright Automated Capture & Testing Matrix

This repository enforces strict CI validation rules and generates optimized, structural visual assets iteratively using Playwright Python across local Chromium instances.

## Requirements

The execution assumes a **locked Python 3.14 context** managed natively through `uv`. All binaries and headless browser requirements are bundled internally if the `uv run` mechanism is utilized.

```bash
# Verify uv environment
uv --version
```

## Running the Social Media Matrix Capture

`capture_social_video.py` launches concurrent Chromium instances, forces local storage overrides for the three A/B CTA testing variants (`[control, var_A, var_B]`), and synchronously captures 12-second WebM 720p clips.

**Execution:**
```bash
# This forces the script to boot isolated into 3.14 pulling inline specs
uv run --python 3.14 capture_social_video.py
```

Outputs (`hero_demo_*.webm`) dump directly to the root execution context directory.

## Running Visual DOM Overlap Assertions

To systematically evaluate overlapping CSS or viewport anomalies when swapping typography across the variations, trigger the assertion layer:

```bash
uv run --python 3.14 visual_assertions.py
```

This guarantees structural integrity on the `<div id="ab-cta-text">` and performs `.toHaveScreenshot()` matrix crawls across the frontend DOM states before rendering passes.
