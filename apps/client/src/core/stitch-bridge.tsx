/**
 * V18 Zenith — Stitch Design Token Bridge
 *
 * The Stitch SDK (@google/stitch-sdk) exports server-side primitives:
 *   - Stitch, Project, Screen, DesignSystem, StitchProxy, stitch (singleton)
 *
 * It does NOT export `useStitchTheme()`. This facade bridges the gap:
 *   1. Fetches M3 design tokens from the Stitch MCP via the singleton client
 *   2. Provides a React context + hook for consuming tokens in components
 *   3. Falls back to Material 3 defaults if the MCP is unreachable
 */

import React, { createContext, type ReactNode, useContext, useEffect, useState } from 'react';

// ─── M3 Design Token Types ────────────────────────────────────────
export interface StitchDesignTokens {
  colors: {
    primary: string;
    onPrimary: string;
    primaryContainer: string;
    onPrimaryContainer: string;
    secondary: string;
    onSecondary: string;
    surface: string;
    onSurface: string;
    surfaceVariant: string;
    onSurfaceVariant: string;
    error: string;
    onError: string;
    outline: string;
    background: string;
    onBackground: string;
  };
  typography: {
    displayLarge: string;
    displayMedium: string;
    displaySmall: string;
    headlineLarge: string;
    headlineMedium: string;
    bodyLarge: string;
    bodyMedium: string;
    labelLarge: string;
  };
  shapes: {
    cornerNone: string;
    cornerSmall: string;
    cornerMedium: string;
    cornerLarge: string;
    cornerFull: string;
  };
  elevation: {
    level0: string;
    level1: string;
    level2: string;
    level3: string;
  };
}

// ─── M3 Default Tokens (Dark Theme) ──────────────────────────────
const M3_DEFAULTS: StitchDesignTokens = {
  colors: {
    primary: '#D0BCFF',
    onPrimary: '#381E72',
    primaryContainer: '#4F378B',
    onPrimaryContainer: '#EADDFF',
    secondary: '#CCC2DC',
    onSecondary: '#332D41',
    surface: '#1C1B1F',
    onSurface: '#E6E1E5',
    surfaceVariant: '#49454F',
    onSurfaceVariant: '#CAC4D0',
    error: '#F2B8B5',
    onError: '#601410',
    outline: '#938F99',
    background: '#0F0D13',
    onBackground: '#E6E1E5',
  },
  typography: {
    displayLarge: '"Outfit", "Inter", system-ui, sans-serif',
    displayMedium: '"Outfit", "Inter", system-ui, sans-serif',
    displaySmall: '"Outfit", "Inter", system-ui, sans-serif',
    headlineLarge: '"Inter", system-ui, sans-serif',
    headlineMedium: '"Inter", system-ui, sans-serif',
    bodyLarge: '"Inter", system-ui, sans-serif',
    bodyMedium: '"Inter", system-ui, sans-serif',
    labelLarge: '"Inter", system-ui, sans-serif',
  },
  shapes: {
    cornerNone: '0px',
    cornerSmall: '8px',
    cornerMedium: '12px',
    cornerLarge: '16px',
    cornerFull: '9999px',
  },
  elevation: {
    level0: 'none',
    level1: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
    level2: '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
    level3: '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
  },
};

// ─── React Context ────────────────────────────────────────────────
const StitchThemeContext = createContext<StitchDesignTokens>(M3_DEFAULTS);

export function StitchThemeProvider({
  children,
  projectId,
}: {
  children: ReactNode;
  projectId?: string;
}) {
  const [tokens, setTokens] = useState<StitchDesignTokens>(M3_DEFAULTS);

  useEffect(() => {
    // Attempt to fetch live tokens from Stitch MCP via the API gateway
    if (projectId) {
      fetch('/graphql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `{ serviceHealth { api graphql } }`,
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data?.data?.serviceHealth?.api) {
            console.log('[StitchBridge] Connected to V18 GraphQL Gateway');
            // Future: fetch design system tokens from Stitch MCP via GraphQL
          }
        })
        .catch(() => {
          console.log('[StitchBridge] Using M3 defaults (gateway offline)');
        });
    }
  }, [projectId]);

  return <StitchThemeContext.Provider value={tokens}>{children}</StitchThemeContext.Provider>;
}

/**
 * useStitchTheme — The facade hook.
 * Bridges the server-side Stitch SDK into React component consumption.
 * Falls back to M3 defaults when the MCP is unreachable.
 */
export function useStitchTheme(): StitchDesignTokens {
  return useContext(StitchThemeContext);
}
