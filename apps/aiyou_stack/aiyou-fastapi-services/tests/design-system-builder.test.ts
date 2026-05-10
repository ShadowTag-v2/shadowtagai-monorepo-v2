import { DesignSystemBuilder } from '../src/agents/design-system-builder';
import { DesignTokenGenerator } from '../src/services/design-token-generator';

describe('Design System Builder', () => {
  let builder: DesignSystemBuilder;

  beforeEach(() => {
    builder = new DesignSystemBuilder();
  });

  describe('createDesignSystem', () => {
    it('should create a design system with default components', async () => {
      const request = {
        projectName: 'Test Design System',
        framework: 'react' as const,
      };

      const library = await builder.createDesignSystem(request);

      expect(library).toBeDefined();
      expect(library.name).toBe('Test Design System');
      expect(library.framework).toBe('react');
      expect(library.components).toBeInstanceOf(Array);
      expect(library.designTokens).toBeDefined();
    });

    it('should create a design system with custom theme', async () => {
      const request = {
        projectName: 'Custom Theme System',
        framework: 'react' as const,
        theme: {
          primaryColor: '#ff0000',
          secondaryColor: '#00ff00',
          fontFamily: 'Roboto',
        },
      };

      const library = await builder.createDesignSystem(request);

      expect(library.designTokens).toBeDefined();
      expect(library.designTokens.colors).toBeInstanceOf(Array);
      expect(library.designTokens.typography).toBeInstanceOf(Array);
    });
  });
});

describe('Design Token Generator', () => {
  let generator: DesignTokenGenerator;

  beforeEach(() => {
    generator = new DesignTokenGenerator();
  });

  describe('generateDesignTokens', () => {
    it('should generate complete design tokens', () => {
      const tokens = generator.generateDesignTokens({
        primaryColor: '#3b82f6',
        secondaryColor: '#8b5cf6',
        fontFamily: 'Inter',
      });

      expect(tokens).toBeDefined();
      expect(tokens.colors).toBeInstanceOf(Array);
      expect(tokens.typography).toBeInstanceOf(Array);
      expect(tokens.spacing).toBeInstanceOf(Array);
      expect(tokens.borderRadius).toBeDefined();
      expect(tokens.shadows).toBeDefined();
      expect(tokens.breakpoints).toBeDefined();
    });

    it('should generate primary color scale', () => {
      const tokens = generator.generateDesignTokens({
        primaryColor: '#3b82f6',
      });

      const primaryColors = tokens.colors.filter((c) => c.category === 'primary');
      expect(primaryColors.length).toBeGreaterThan(0);
      expect(primaryColors.some((c) => c.name === 'primary-500')).toBe(true);
    });

    it('should generate typography tokens', () => {
      const tokens = generator.generateDesignTokens({
        fontFamily: 'Inter',
      });

      expect(tokens.typography.length).toBeGreaterThan(0);
      expect(tokens.typography[0]).toHaveProperty('name');
      expect(tokens.typography[0]).toHaveProperty('fontSize');
      expect(tokens.typography[0]).toHaveProperty('fontWeight');
      expect(tokens.typography[0]).toHaveProperty('lineHeight');
      expect(tokens.typography[0]).toHaveProperty('fontFamily');
    });

    it('should generate spacing tokens with correct scale', () => {
      const tokens = generator.generateDesignTokens({});

      expect(tokens.spacing.length).toBeGreaterThan(0);
      expect(tokens.spacing[0]).toHaveProperty('name');
      expect(tokens.spacing[0]).toHaveProperty('value');
      expect(tokens.spacing[0]).toHaveProperty('scale');
    });
  });
});
