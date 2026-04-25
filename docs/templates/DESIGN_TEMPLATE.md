---
version: alpha
name: "[App Name] Design System"
description: "[Brief description of the visual identity and brand personality]"
colors:
  # Core palette — semantic roles, NOT decorative names
  primary: "#1A1C1E"           # Main text/ink color
  on-primary: "#FFFFFF"        # Text ON primary-colored surfaces
  secondary: "#6C7278"         # Supporting content (borders, captions)
  tertiary: "#B8422E"          # Accent/interaction (CTAs, highlights)
  neutral: "#F7F5F2"           # Canvas/background surface
  surface: "#FFFFFF"           # Card/container backgrounds
  on-surface: "#1A1C1E"       # Text on surface backgrounds
  error: "#BA1A1A"             # Error indicators
  # Add domain-specific tokens below:
  # status-success: "#00E676"
  # status-warning: "#FFB347"
typography:
  headline-display:
    fontFamily: Inter
    fontSize: 64px
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 600
    lineHeight: 1.3
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1
    letterSpacing: 0.02em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.04em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.05em
rounded:
  none: 0px
  sm: 4px
  md: 8px
  lg: 12px
  xl: 16px
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
  gutter: 24px
  margin: 32px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.md}"
    height: 44px
    padding: 0 24px
  button-primary-hover:
    backgroundColor: "{colors.tertiary}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.md}"
    height: 44px
    padding: 0 24px
  card-standard:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  input-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    height: 44px
    padding: 0 16px
---

## Overview

<!-- Replace with your design rationale and brand personality description -->

This design system establishes the visual identity for [App Name]. The aesthetic
is [describe mood — e.g., "clean and authoritative" or "warm and approachable"].
The target audience is [describe] and the interface should evoke [emotional response].

## Colors

<!-- Describe each color's purpose and character using natural language -->

- **Primary (#1A1C1E):** [Describe role — e.g., "Deep ink for headlines and core text"]
- **Secondary (#6C7278):** [Describe role — e.g., "Sophisticated slate for borders and metadata"]
- **Tertiary (#B8422E):** [Describe role — e.g., "Accent color for CTAs and highlights"]
- **Neutral (#F7F5F2):** [Describe role — e.g., "Warm canvas for page backgrounds"]

## Typography

<!-- Describe font strategy and hierarchy reasoning -->

The typography uses **Inter** for [reason]. Headlines use [weight] to convey
[feeling]. Body text at [size] ensures readability for [context].

## Layout

<!-- Describe spacing strategy, grid model, and rhythm -->

The layout follows a [grid model] with an [N]px base spacing scale.
[Describe containment, grouping, and negative space philosophy.]

## Elevation & Depth

<!-- Describe how visual hierarchy is conveyed -->

[Describe shadow strategy, layering, or flat design approach.]

## Shapes

<!-- Describe corner radius philosophy and shape language -->

The shape language uses [description — e.g., "moderate rounding (8px)"] for
[containers/buttons] to achieve a [feeling — e.g., "modern but structured"] aesthetic.

## Components

### Buttons
Primary buttons use [tertiary accent] as background for maximum contrast.
Secondary buttons use [surface color] with [primary text].

### Cards
Cards use [surface color] with [rounded corners] and [shadow/border strategy].

### Inputs
Text inputs use [background] with [border strategy] and [focus style].

## Do's and Don'ts

- Do use the accent color only for the most important action per screen
- Do maintain WCAG AA contrast ratios (4.5:1 for normal text)
- Don't hardcode hex values in component code — use token references
- Don't mix rounded and sharp corners in the same view
- Don't use more than two font weights on a single screen
