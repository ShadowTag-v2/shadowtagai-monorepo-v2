# Implementation Plan - UphillSnowball Matrix (Pickle Protocol)

Injecting the UphillSnowball Economic Matrix into the `shadowtag-web` frontend using the structural skeleton hijacked from `unusualmachines.com`.

## User Review Required

> [!IMPORTANT]
> The "Pickle Protocol" involves replicating the structural geometry of `unusualmachines.com`. I have extracted the DOM and layout patterns and will apply them to our Next.js components.

## Proposed Changes

### [Frontend] shadowtag-web

#### [MODIFY] [GlowButton.tsx](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/components/ui/GlowButton.tsx)

- Add `gold` variant (`#b58900`) and `crimson` variant (`#dc322f`).

#### [MODIFY] [Navbar.tsx](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/components/hero/Navbar.tsx)

- Update link labels to: "Foundation", "Zero Series", "Citadels", "Armory", "Apex".
- Update logo to "UphillSnowball".

#### [MODIFY] [HeroContent.tsx](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/components/hero/HeroContent.tsx)

- Inject UphillSnowball economic engine copy.
- Apply Gold gradient text clip.

#### [NEW] [FinancialTicker.tsx](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/components/hero/FinancialTicker.tsx)

- Implement a horizontal scrolling banner with Web3/UphillSnowball metrics.

#### [NEW] [CitadelGrid.tsx](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/components/hero/CitadelGrid.tsx)

- 3-column grid for Justitia, Caduceus, and Omniscience citadels.

#### [NEW] [UphillSnowballWidgets.tsx](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/components/ui/UphillSnowballWidgets.tsx)

- `UphillSnowballCartWidget`: Interactive enterprise pricing cart.
- `NightlyBriefingWidget`: Layer 0 ROI briefing dashboard.

#### [MODIFY] [page.tsx](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/app/page.tsx)

- Assemble `Navbar`, `HeroContent`, `FinancialTicker`, and `CitadelGrid`.

## Verification Plan

### Automated Tests

- `npm run lint` in `apps/shadowtag-web`.

### Manual Verification

- Deploy to local dev and verify the "Dark Luxury" aesthetic and structural alignment with Unusual Machines.
