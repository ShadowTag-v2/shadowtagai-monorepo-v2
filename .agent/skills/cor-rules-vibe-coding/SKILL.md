# Cor.Rules for Vibe Coding v1.0

**Activation**: Auto-load when editing React/TypeScript components, writing frontend code, or generating UI.

---

## Security Rules (Non-Negotiable)

1. **No `eval()` or `Function()` on user input** — XSS vector. Use JSON.parse with try/catch.
2. **No `dangerouslySetInnerHTML`** without explicit DOMPurify sanitization.
3. **No `innerHTML` assignment** — use `textContent` or React's JSX.
4. **No secrets in client bundles** — `NEXT_PUBLIC_*` only for truly public values.
5. **No `localStorage` for auth tokens** — use httpOnly cookies.
6. **No dynamic `import()` of user-controlled strings**.
7. **No `target="_blank"` without `rel="noopener noreferrer"`**.
8. **No direct `fetch()` to third-party URLs from SSR** without allowlist.
9. **Validate all props with Zod/Pydantic at system boundaries** — not just TypeScript types.
10. **No `.env` values committed** — always `.env.local` / Secret Manager.

---

## Atomic Design Component Rules

### Size Limits (enforce strictly)
| Layer | Max Lines | Max Props | Rule |
|-------|-----------|-----------|------|
| Atom | 50 | 5 | Single HTML element, zero business logic |
| Molecule | 100 | 8 | Composed atoms, single responsibility |
| Organism | 150 | 12 | Full feature section, owns local state |
| Template | 200 | 6 | Layout only, no data fetching |
| Page | 80 | 4 | Route handler, composes organisms |

**When a component exceeds its limit → extract immediately, do not refactor later.**

### Extraction Triggers
- Logic > 20 lines in JSX → move to custom hook `use[Name].ts`
- 3+ related state vars → consolidate to `useReducer` or Zustand slice
- Same JSX block repeated ≥ 2 times → extract to Atom/Molecule
- Prop drilling > 2 levels → Context or Zustand

---

## Vercel / Next.js React Best Practices

### Data Fetching
- **Server Components by default** — only add `'use client'` when you need interactivity/browser APIs
- **`fetch()` with `{ next: { revalidate: N } }`** for ISR — never `getServerSideProps` in App Router
- **Parallel fetching with `Promise.all`** — never sequential `await` chains for independent requests
- **`<Suspense>` boundaries per data dependency** — granular, not page-level

### Performance
- **Images**: always `next/image` with explicit `width`/`height` or `fill` + `sizes`
- **Fonts**: `next/font` with `display: 'swap'` — never `<link>` in `<head>`
- **Bundle**: `next/dynamic` with `{ ssr: false }` for heavy client-only libs (charts, editors)
- **Prefetch**: `<Link prefetch>` for high-probability nav targets only

### State Management Hierarchy
1. **URL state** (search params) — shareable, bookmarkable
2. **Server state** (React Query / SWR) — cache, deduplicate
3. **Local component state** (`useState`) — ephemeral UI
4. **Global client state** (Zustand) — cross-component, not server-derivable

Never reach for Zustand if URL state or server state covers the use case.

### Error Handling
- Every `async` Server Component wrapped in `error.tsx` at its route segment
- `<ErrorBoundary>` around every `<Suspense>` with client-side data
- Never swallow errors silently — log with `structlog` / `console.error` at minimum

---

## ESLint Hybrid Setup

```jsonc
// .eslintrc hybrid (ESLint + Biome co-exist)
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended-type-checked"
  ],
  "rules": {
    // Security
    "no-eval": "error",
    "react/no-danger": "error",
    // Atomic Design size — use eslint-plugin-react-complexity or custom rule
    "max-lines": ["warn", { "max": 150, "skipBlankLines": true }],
    // Hooks
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    // Imports
    "@typescript-eslint/no-floating-promises": "error",
    "@typescript-eslint/await-thenable": "error"
  }
}
```

**Biome handles**: formatting, import sorting, simple lint rules (fast, pre-commit).
**ESLint handles**: type-aware rules (`recommended-type-checked`), React-specific, security.

---

## Stack Recommendations (PNKLN / Antigravity)

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Framework | Next.js 15 App Router | RSC, streaming, Vercel-native |
| Styling | Tailwind v4 | Co-located, purged, JIT |
| State | Zustand + URL params | Minimal, no boilerplate |
| Forms | React Hook Form + Zod | Type-safe, zero re-renders |
| Data | TanStack Query v5 | Server/client cache unified |
| Testing | Vitest + Testing Library | Fast, RSC-compatible |
| Lint | Biome (format) + ESLint (type) | Best of both |
| Icons | Lucide React | Tree-shakeable |

---

## Custom Hooks Extraction Pattern

```typescript
// ❌ Logic buried in component
function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  useEffect(() => { /* 30 lines of fetch logic */ }, [])
  // ...
}

// ✅ Extracted hook
// hooks/useDashboardData.ts
export function useDashboardData(runId: string) {
  return useQuery({ queryKey: ['dashboard', runId], queryFn: () => fetchDashboard(runId) })
}

function Dashboard() {
  const { data, isLoading, error } = useDashboardData(runId)
  // Component is now pure layout
}
```

---

## 20 Vibe Coding Pitfalls to Avoid

1. Accepting first-draft code without reading it
2. Not running the code before moving on
3. Context window overflow — use `/compact` or dev docs before limit
4. Skipping tests ("I'll add them later")
5. Over-abstracting on first pass
6. Generating UI without a design reference
7. Letting state management sprawl (`useState` everywhere)
8. `any` types proliferating — treat as build error
9. Missing `loading` and `error` states in every async component
10. Hardcoding URLs / API keys in components
11. Prop drilling instead of proper state architecture
12. Ignoring accessibility (`aria-*`, keyboard nav, color contrast)
13. SSR/client mismatch from browser-only APIs in Server Components
14. Not memoizing expensive renders (`useMemo`, `React.memo`)
15. Committing without gitleaks scan (already enforced in sync-daemon)
16. Skipping planning mode for features > 2 files
17. Generating boilerplate without checking existing utilities
18. Not updating dev docs context file after architectural decisions
19. Deploying without checking bundle size (`next build` analyzer)
20. Forgetting `revalidatePath` / `revalidateTag` after server mutations

---

## Agent Skill Triggers

Auto-activate this skill when:
- Editing `*.tsx`, `*.jsx`, `*.ts` files in `apps/` or `src/`
- Writing new React components
- Reviewing PRs that touch frontend
- User mentions "component", "hook", "Tailwind", "Next.js", "Vercel"

---

**Version**: 1.0
**Last Updated**: 2026-03-24
**Owner**: Antigravity / PNKLN Architecture Team
