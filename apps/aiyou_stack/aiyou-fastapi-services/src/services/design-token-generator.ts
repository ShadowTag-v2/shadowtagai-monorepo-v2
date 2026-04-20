import type {
  ColorToken,
  DesignTokens,
  SpacingToken,
  TypographyToken,
} from '../types/design-system';

export class DesignTokenGenerator {
  /**
   * Generate a complete set of design tokens based on primary theme colors
   */
  generateDesignTokens(options: {
    primaryColor?: string;
    secondaryColor?: string;
    fontFamily?: string;
  }): DesignTokens {
    const primaryColor = options.primaryColor || '#3b82f6'; // Default blue
    const secondaryColor = options.secondaryColor || '#8b5cf6'; // Default purple
    const fontFamily = options.fontFamily || 'Inter, system-ui, -apple-system, sans-serif';

    return {
      colors: this.generateColorTokens(primaryColor, secondaryColor),
      typography: this.generateTypographyTokens(fontFamily),
      spacing: this.generateSpacingTokens(),
      borderRadius: this.generateBorderRadius(),
      shadows: this.generateShadows(),
      breakpoints: this.generateBreakpoints(),
    };
  }

  /**
   * Generate comprehensive color tokens with primary, secondary, neutral, and semantic colors
   */
  private generateColorTokens(primaryColor: string, secondaryColor: string): ColorToken[] {
    return [
      // Primary colors
      { name: 'primary-50', value: this.lighten(primaryColor, 95), category: 'primary' },
      { name: 'primary-100', value: this.lighten(primaryColor, 90), category: 'primary' },
      { name: 'primary-200', value: this.lighten(primaryColor, 80), category: 'primary' },
      { name: 'primary-300', value: this.lighten(primaryColor, 60), category: 'primary' },
      { name: 'primary-400', value: this.lighten(primaryColor, 40), category: 'primary' },
      {
        name: 'primary-500',
        value: primaryColor,
        category: 'primary',
        description: 'Primary brand color',
      },
      { name: 'primary-600', value: this.darken(primaryColor, 20), category: 'primary' },
      { name: 'primary-700', value: this.darken(primaryColor, 40), category: 'primary' },
      { name: 'primary-800', value: this.darken(primaryColor, 60), category: 'primary' },
      { name: 'primary-900', value: this.darken(primaryColor, 80), category: 'primary' },

      // Secondary colors
      { name: 'secondary-50', value: this.lighten(secondaryColor, 95), category: 'secondary' },
      { name: 'secondary-100', value: this.lighten(secondaryColor, 90), category: 'secondary' },
      { name: 'secondary-200', value: this.lighten(secondaryColor, 80), category: 'secondary' },
      { name: 'secondary-300', value: this.lighten(secondaryColor, 60), category: 'secondary' },
      { name: 'secondary-400', value: this.lighten(secondaryColor, 40), category: 'secondary' },
      {
        name: 'secondary-500',
        value: secondaryColor,
        category: 'secondary',
        description: 'Secondary brand color',
      },
      { name: 'secondary-600', value: this.darken(secondaryColor, 20), category: 'secondary' },
      { name: 'secondary-700', value: this.darken(secondaryColor, 40), category: 'secondary' },
      { name: 'secondary-800', value: this.darken(secondaryColor, 60), category: 'secondary' },
      { name: 'secondary-900', value: this.darken(secondaryColor, 80), category: 'secondary' },

      // Neutral colors
      { name: 'neutral-50', value: '#fafafa', category: 'neutral' },
      { name: 'neutral-100', value: '#f5f5f5', category: 'neutral' },
      { name: 'neutral-200', value: '#e5e5e5', category: 'neutral' },
      { name: 'neutral-300', value: '#d4d4d4', category: 'neutral' },
      { name: 'neutral-400', value: '#a3a3a3', category: 'neutral' },
      { name: 'neutral-500', value: '#737373', category: 'neutral' },
      { name: 'neutral-600', value: '#525252', category: 'neutral' },
      { name: 'neutral-700', value: '#404040', category: 'neutral' },
      { name: 'neutral-800', value: '#262626', category: 'neutral' },
      { name: 'neutral-900', value: '#171717', category: 'neutral' },

      // Semantic colors
      { name: 'success', value: '#10b981', category: 'semantic', description: 'Success state' },
      { name: 'warning', value: '#f59e0b', category: 'semantic', description: 'Warning state' },
      { name: 'error', value: '#ef4444', category: 'semantic', description: 'Error state' },
      { name: 'info', value: '#3b82f6', category: 'semantic', description: 'Info state' },
    ];
  }

  /**
   * Generate typography tokens with a type scale
   */
  private generateTypographyTokens(fontFamily: string): TypographyToken[] {
    return [
      {
        name: 'display-2xl',
        fontSize: '4.5rem',
        fontWeight: 'bold',
        lineHeight: '1.1',
        letterSpacing: '-0.02em',
        fontFamily,
      },
      {
        name: 'display-xl',
        fontSize: '3.75rem',
        fontWeight: 'bold',
        lineHeight: '1.1',
        letterSpacing: '-0.02em',
        fontFamily,
      },
      {
        name: 'display-lg',
        fontSize: '3rem',
        fontWeight: 'bold',
        lineHeight: '1.2',
        letterSpacing: '-0.01em',
        fontFamily,
      },
      {
        name: 'heading-xl',
        fontSize: '2.25rem',
        fontWeight: 600,
        lineHeight: '1.3',
        fontFamily,
      },
      {
        name: 'heading-lg',
        fontSize: '1.875rem',
        fontWeight: 600,
        lineHeight: '1.3',
        fontFamily,
      },
      {
        name: 'heading-md',
        fontSize: '1.5rem',
        fontWeight: 600,
        lineHeight: '1.4',
        fontFamily,
      },
      {
        name: 'heading-sm',
        fontSize: '1.25rem',
        fontWeight: 600,
        lineHeight: '1.4',
        fontFamily,
      },
      {
        name: 'body-lg',
        fontSize: '1.125rem',
        fontWeight: 400,
        lineHeight: '1.6',
        fontFamily,
      },
      {
        name: 'body-md',
        fontSize: '1rem',
        fontWeight: 400,
        lineHeight: '1.6',
        fontFamily,
      },
      {
        name: 'body-sm',
        fontSize: '0.875rem',
        fontWeight: 400,
        lineHeight: '1.5',
        fontFamily,
      },
      {
        name: 'caption',
        fontSize: '0.75rem',
        fontWeight: 400,
        lineHeight: '1.4',
        fontFamily,
      },
    ];
  }

  /**
   * Generate spacing tokens using a consistent scale (8px base)
   */
  private generateSpacingTokens(): SpacingToken[] {
    const baseUnit = 8; // 8px base
    const scales = [0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32];

    return scales.map((scale) => ({
      name: `spacing-${scale === 0.5 ? '0-5' : scale}`,
      value: `${baseUnit * scale}px`,
      scale,
    }));
  }

  /**
   * Generate border radius tokens
   */
  private generateBorderRadius(): Record<string, string> {
    return {
      none: '0',
      sm: '0.125rem',
      md: '0.375rem',
      lg: '0.5rem',
      xl: '0.75rem',
      '2xl': '1rem',
      '3xl': '1.5rem',
      full: '9999px',
    };
  }

  /**
   * Generate shadow tokens
   */
  private generateShadows(): Record<string, string> {
    return {
      xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
      sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
      md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
      lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
      xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
      '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
      none: 'none',
    };
  }

  /**
   * Generate responsive breakpoints
   */
  private generateBreakpoints(): Record<string, string> {
    return {
      xs: '320px',
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
    };
  }

  /**
   * Lighten a hex color by percentage
   */
  private lighten(hex: string, percent: number): string {
    const num = parseInt(hex.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) + amt;
    const G = ((num >> 8) & 0x00ff) + amt;
    const B = (num & 0x0000ff) + amt;

    return (
      '#' +
      (
        0x1000000 +
        (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
        (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
        (B < 255 ? (B < 1 ? 0 : B) : 255)
      )
        .toString(16)
        .slice(1)
    );
  }

  /**
   * Darken a hex color by percentage
   */
  private darken(hex: string, percent: number): string {
    const num = parseInt(hex.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) - amt;
    const G = ((num >> 8) & 0x00ff) - amt;
    const B = (num & 0x0000ff) - amt;

    return (
      '#' +
      (
        0x1000000 +
        (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
        (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
        (B < 255 ? (B < 1 ? 0 : B) : 255)
      )
        .toString(16)
        .slice(1)
    );
  }
}
