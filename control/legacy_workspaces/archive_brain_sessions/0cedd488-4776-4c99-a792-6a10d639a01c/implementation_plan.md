# Exact Replication of Unusual Machines Aesthetic

Phase 21 initially requested a "Structural hijack into UphillNav... Next.js page.tsx routing rewrite for Dark Luxury Web3 UI". As a result, the application was built using a cinematic dark mode, video backgrounds, glowing buttons, and a grid overlay.

To exactly copy the visual identity of `https://www.unusualmachines.com/`, we must perform a complete structural tear-down of the current `page.tsx` and switch to a light-themed, corporate, and highly accessible layout.

## User Review Required

> [!WARNING]
> This will entirely replace the Dark Luxury Web3 Aesthetic with a standard Light Corporate Aesthetic.
>
> Regarding your question on the **Chrome DevTools MCP**: I am **NOT** using `chrome-devtools-mcp`. It is not instantiated in my internal context, nor is it configured in the `mcp_servers.json` on this machine. My current active MCPs are limited to Stitch, BigQuery, Cloud SQL, Cloud Run, Dart, and Dataplex. If you would like me to use the Chrome DevTools MCP to natively inspect elements, we need to install and configure it in your global cursor/gemini settings.

## Proposed Changes

### Next.js Frontend (`shadowtag-web`)

#### [MODIFY] [page.tsx](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/app/page.tsx)
- **Remove:** The background `<video>`, `CitadelGrid`, ambient overlays, and `FinancialTicker`.
- **Implement:** A clean, white/light-gray background layout.
- **Structure:**
  1. A minimal corporate Header/Navbar.
  2. A clean Hero Section with the Leaf Logo and high-contrast text.
  3. A 3-column "Recent News / Quick Links / Upcoming Events" section.
  4. The "Judge 6" compliance matrix and "About Us" section styled cleanly with standard sans-serif typography.
  5. The structured Contact / Investor / Media footer.

#### [MODIFY] [Navbar.tsx](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/components/hero/Navbar.tsx)
- Remove `GlowButton` and absolute positioning.
- Use a `bg-white text-black` sticky top-nav matching the strict unusualmachines.com header.

#### [MODIFY] [AboutSection.tsx](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/components/AboutSection.tsx) & [TeamSection.tsx](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/components/TeamSection.tsx)
- Strip out `bg-black/50`, `backdrop-blur-xl`, and `border-white/10`.
- Replace with crisp `bg-white text-gray-900` styling, using light-gray borders and standard corporate padding.

## Verification Plan

### Automated Tests
- Run `npm run lint` and `npm run build` on `apps/shadowtag-web` to ensure no Typescript or strict-mode Next.js errors are introduced.

### Manual Verification
- We will boot the localhost server (`npm run dev`) and I will capture another screenshot using `capture-website-cli` so you can visually confirm the new light corporate design perfectly matches the visual structure of unusualmachines.com.
