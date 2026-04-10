
# Implementation Plan - Stitch Native (UphillSnowball RN)

## User Review Required
> [!NOTE]
> **Source:** Porting `src/monetization/landing_page.py` (HTML/CSS) to React Native.
> **Scope:** Converting the "Commercial Node" landing page (Hero, Pricing, ROI) into a reusable React Native component (`UphillSnowball`).
> **Tech:** Expo (React Native), NativeWind (Tailwind for RN) if available, or StyleSheet.

## Proposed Changes

### [NEW] `apps/stitch_native`
Initialize a new Expo project to host the Stitch Native components.

#### [NEW] `apps/stitch_native/components/UphillSnowball.tsx`
- **Hero Section:** Gradient background, title, stats grid.
- **Features Section:** Card list with icons.
- **Pricing Section:** Horizontal scroll or vertical list of pricing cards.
- **ROI Calculator:** Interactive stateful component (Input fields + instant calculation).
- **Footer:** Simple links.

### Testing Strategy
- **Unit Tests:** `jest` + `react-test-renderer` to snapshot and verify component rendering.
- **Run:** `npm test` in `apps/stitch_native`.

### Design Options
1. **Sentinel Cyberpunk:** Dark mode, neon accents, matrix event logs.
2. **Corporate Glass:** Glassmorphism, light/soft dark mode, clean typography.

### Logic Conversion
- Convert Python `generate_landing_page` HTML structure to `<ScrollView>`, `<View>`, `<Text>`.
- Convert CSS gradients to `expo-linear-gradient`.
- Convert JavaScript ROI logic to React state (`useState`).

## Verification Plan

### Manual Verification
- Run `npx expo start --web` to verify layout in browser (fastest).
- If possible, run on iOS Simulator (optional, depends on environment).
