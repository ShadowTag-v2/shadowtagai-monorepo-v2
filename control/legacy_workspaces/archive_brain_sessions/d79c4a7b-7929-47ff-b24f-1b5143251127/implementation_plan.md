# reCAPTCHA Integration Plan

The user requested fixing the Google reCAPTCHA integrations based on warnings in the GCP console for two keys: `shadowtag-web-key` and `sovereign-shield-key`.

## Proposed Changes

### shadowtag-web (`apps/shadowtag-web`)
The `shadowtag-web-key` matches this app.
Site Key: `6LeBmGksAAAAAKHaelFgvyTLC7iPGXf6GefAJkDp`

#### [MODIFY] layout.tsx (file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/app/layout.tsx)
- Add `import Script from 'next/script';`
- Add the reCAPTCHA v3/Enterprise script tag to load globally and score traffic:
  ```tsx
  <Script
    src="https://www.google.com/recaptcha/api.js?render=6LeBmGksAAAAAKHaelFgvyTLC7iPGXf6GefAJkDp"
    strategy="beforeInteractive"
  />
  ```

### stitch_dashboard
The `sovereign-shield-key` likely corresponds to the Sovereign Operations / Dashboard.
Site Key: `6Lej92UsAAAAAM3v7gRytCt_IXz_-CxffCeXYdKO`

#### [MODIFY] layout.tsx (file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/stitch_dashboard/app/layout.tsx)
- Add `import Script from 'next/script';`
- Add the reCAPTCHA script tag:
  ```tsx
  <Script
    src="https://www.google.com/recaptcha/api.js?render=6Lej92UsAAAAAM3v7gRytCt_IXz_-CxffCeXYdKO"
    strategy="beforeInteractive"
  />
  ```

## Important Considerations
Currently, these are "Invisible" reCAPTCHA keys that score traffic automatically when the script is loaded with a `render` ID. If you need explicit verification triggered on specific UI buttons (like form submissions or payment flows), we will also need to add `grecaptcha.execute()` calls to those components and send the token to your backend.

*Are there specific forms or API endpoints you need protected by verifying the token, or are we just adding the telemetry script to clear the automated Google Cloud warnings?*

## Verification Plan

### Automated Tests
_None existing for UI rendering of this script._

### Manual Verification
1. Run the local dev server for `shadowtag-web` (`npm run dev` in `apps/shadowtag-web`).
2. Open the page in the browser and inspect the `<head>` or body.
3. Verify that the reCAPTCHA script with the correct `render` query parameter is present.
4. Verify the global `grecaptcha` object is available in the browser console.
5. Check GCP Cloud Console to see if the warnings clear after traffic is detected.
