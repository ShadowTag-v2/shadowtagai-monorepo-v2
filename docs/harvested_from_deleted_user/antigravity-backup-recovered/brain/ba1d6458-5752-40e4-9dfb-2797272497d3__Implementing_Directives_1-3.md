# Implementing Directives 1-3

## Directive 1: Splinter Syndication Engine

- [x] Create [apps/src/distribution/splinter_adk_agent.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/src/distribution/splinter_adk_agent.py) with the provided code.

## Directive 2: Dual-Core Terminal Demo Artifacts

- [x] Create [apps/src/components/ActivistDashboard.tsx](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/src/components/ActivistDashboard.tsx) (Glassmorphism UI variant).
- [x] Create/Update [apps/src/api/auth.ts](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/src/api/auth.ts) to ensure `NEXT_PUBLIC_STRIPE_SECRET` is NOT exposed, using `process.env.STRIPE_SECRET` instead.

## Directive 3: 10-Fingers Activist Script

- [x] Create [apps/src/agents/activist/raider_oracle.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/src/agents/activist/raider_oracle.py) with the provided code.

## Directive 4: Copilot Backend Configuration

- [x] Update [apps/uphillsnowball/web/app/api/copilotkit/route.ts](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/uphillsnowball/web/app/api/copilotkit/route.ts) to use `AnthropicAdapter`.
- [x] Configure `AnthropicAdapter` to run Claude Opus (e.g. `claude-3-opus-20240229`).

## Directive 5: ShadowTag Web Homepage Assembly

- [x] Step 1: Mount the Arsenal (Integrate [TeamSection](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/components/TeamSection.tsx#32-135), [Judge6Section](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/components/Judge6Section.tsx#86-196), or [DeckViewer](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/components/DeckViewer.tsx#18-125) natively into [page.tsx](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/app/page.tsx)).
- [x] Step 2: Flesh out the 3 Columns (Replace placeholders for "Recent News" and "Quick Links" with real stylistic components/data).
- [x] Step 3: Integrate the Copilot (Wire up the [ActivistDashboard.tsx](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/src/components/ActivistDashboard.tsx) Copilot UI).
- [ ] Step 4: Polish & Deploy (Boot `npm run dev` server to visually QA the fluid waves).

## Verification

- [ ] Run `npm run lint` and `npm run metrics` in `ShadowTag-v2/apps` to honor CodePMCS Golden Rules.
