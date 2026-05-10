# Next.js Asset Optimization Playbook

To adhere to Vercel best practices regarding optimal asset delivery for the ShadowTagAI payload:

## Image Loading
1. **Prioritize LCP**: The hero image or generative background MUST contain the `priority` flag (`<Image priority />`) to skip lazy loading and guarantee it lands in the LCP window.
2. **Format Optimization**: Ensure `next/image` is outputting WebP or AVIF formats.

## Pre-fetching & Bundles
1. **Link Pre-fetching**: By default, Next.js `<Link>` components prefetch resources in the background. If rendering massive lists, disable pre-fetching (`prefetch={false}`) for items below the fold to conserve network bridging.
2. **Tree Shaking**: Ensure massive libraries (e.g., Lodash or D3) are imported via named exports to trigger aggressive dead-code elimination.

## Font Optimization
Utilize `next/font/google` to embed fonts directly during build time, totally eliminating layout shifts (CLS) caused by subsequent remote font downloads.
