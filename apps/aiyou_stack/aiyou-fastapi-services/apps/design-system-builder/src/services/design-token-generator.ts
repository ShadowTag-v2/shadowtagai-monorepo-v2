/**
 * DOCTRINE: Design System Builder Agent
 * COMPONENT: Design Token Generator
 * FEATURES: Colors, Typography, Spacing, Breakpoints
 */

export interface ThemeConfig {
  primaryColor: string;
  secondaryColor: string;
  baseSpace: number; // usually 8
}

export class DesignTokenGenerator {
  generateTokens(config: ThemeConfig) {
    return {
      colors: this.generateColorScale(config.primaryColor, config.secondaryColor),
      spacing: this.generateSpacing(config.baseSpace),
      typography: {
        fontFamily: "Inter, system-ui, sans-serif",
        scale: this.generateTypeScale(),
      },
      breakpoints: {
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
      },
    };
  }

  private generateColorScale(primary: string, secondary: string) {
    // Mock generation of 50-900 scale
    return {
      primary: {
        500: primary,
        main: primary,
      },
      secondary: {
        500: secondary,
        main: secondary,
      },
      neutral: "#1e293b", // Slate-800
    };
  }

  private generateSpacing(base: number) {
    return {
      1: `${base}px`,
      2: `${base * 2}px`,
      4: `${base * 4}px`,
      8: `${base * 8}px`,
    };
  }

  private generateTypeScale() {
    return {
      h1: "2.5rem",
      h2: "2.0rem",
      h3: "1.75rem",
      body: "1.0rem",
    };
  }
}
