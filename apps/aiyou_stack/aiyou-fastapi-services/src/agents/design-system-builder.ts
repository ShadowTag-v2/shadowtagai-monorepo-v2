import { designSystemBuilderConfig } from '../config/agent-config';
import { ComponentScaffolder } from '../services/component-scaffolder';
import { DesignTokenGenerator } from '../services/design-token-generator';
import type {
  Component,
  ComponentLibrary,
  DesignSystemRequest,
  DesignTokens,
} from '../types/design-system';
import { logger } from '../utils/logger';

export class DesignSystemBuilder {
  private tokenGenerator: DesignTokenGenerator;
  private componentScaffolder: ComponentScaffolder;

  constructor() {
    this.tokenGenerator = new DesignTokenGenerator();
    this.componentScaffolder = new ComponentScaffolder();
  }

  /**
   * Create a complete design system based on request
   */
  async createDesignSystem(request: DesignSystemRequest): Promise<ComponentLibrary> {
    logger.info(`Creating design system: ${request.projectName}`);

    try {
      // Generate design tokens
      const designTokens = this.tokenGenerator.generateDesignTokens({
        primaryColor: request.theme?.primaryColor,
        secondaryColor: request.theme?.secondaryColor,
        fontFamily: request.theme?.fontFamily,
      });

      // Generate components using AI or defaults
      const components = await this.generateComponents(request, designTokens);

      // Create component library
      const library: ComponentLibrary = {
        name: request.projectName,
        version: '1.0.0',
        framework: request.framework,
        components,
        designTokens,
        styleGuide: {
          brandGuidelines: `Design system for ${request.projectName}`,
          usagePatterns: 'Follow component prop interfaces and design tokens',
          bestPractices: 'Use semantic tokens, maintain consistency, ensure accessibility',
        },
      };

      // Scaffold the library
      await this.scaffoldLibrary(library);

      logger.info(`Design system created successfully: ${request.projectName}`);
      return library;
    } catch (error) {
      logger.error('Error creating design system:', error);
      throw error;
    }
  }

  /**
   * Generate components using Claude AI (optional) or fallback to defaults
   */
  private async generateComponents(
    request: DesignSystemRequest,
    designTokens: DesignTokens,
  ): Promise<Component[]> {
    const componentNames = request.components || this.getDefaultComponents();

    // For now, use default components
    // AI integration can be enabled when ANTHROPIC_API_KEY is configured
    if (!process.env.ANTHROPIC_API_KEY) {
      logger.info('ANTHROPIC_API_KEY not configured, using default components');
      return this.generateDefaultComponents(componentNames, request.framework);
    }

    // AI-powered generation would go here
    // Currently commented out until SDK configuration is properly set up
    /*
    const prompt = `Generate ${componentNames.length} components for a ${request.framework} design system.

Framework: ${request.framework}
Components needed: ${componentNames.join(', ')}

Design Tokens Available:
- Colors: ${designTokens.colors.length} color tokens
- Typography: ${designTokens.typography.length} type styles
- Spacing: ${designTokens.spacing.length} spacing values

Requirements:
${request.features?.darkMode ? '- Support dark mode' : ''}
${request.features?.responsive ? '- Fully responsive design' : ''}
${request.features?.accessibility ? '- WCAG 2.1 AA compliant' : ''}
${request.features?.animations ? '- Include smooth animations' : ''}

For each component, provide:
1. Component name
2. Category (layout, input, display, feedback, navigation, or overlay)
3. Description
4. Props interface with types, required flags, and descriptions
5. Accessibility considerations

Return the components as a JSON array.`;

    try {
      // Call Claude Agent SDK here
      // const result = await query({ prompt });
      // return this.parseComponentsFromAIResponse(result, componentNames);
    } catch (error) {
      logger.warn('AI generation failed, using default components:', error);
    }
    */

    return this.generateDefaultComponents(componentNames, request.framework);
  }

  /**
   * Parse components from AI response
   */
  private parseComponentsFromAIResponse(response: string, componentNames: string[]): Component[] {
    try {
      // Try to extract JSON from response
      const jsonMatch = response.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      logger.warn('Failed to parse AI response, using defaults');
    }
    return this.generateDefaultComponents(componentNames, 'react');
  }

  /**
   * Generate default components when AI generation fails
   */
  private generateDefaultComponents(componentNames: string[], framework: string): Component[] {
    const defaultComponents: Record<string, Partial<Component>> = {
      Button: {
        category: 'input',
        description: 'A versatile button component with multiple variants',
        props: [
          {
            name: 'variant',
            type: 'string',
            required: false,
            defaultValue: 'primary',
            description: 'Button style variant',
          },
          {
            name: 'size',
            type: 'string',
            required: false,
            defaultValue: 'medium',
            description: 'Button size',
          },
          {
            name: 'disabled',
            type: 'boolean',
            required: false,
            defaultValue: false,
            description: 'Disabled state',
          },
          { name: 'onClick', type: 'function', required: false, description: 'Click handler' },
          { name: 'children', type: 'ReactNode', required: true, description: 'Button content' },
        ],
      },
      Input: {
        category: 'input',
        description: 'Text input field with validation support',
        props: [
          {
            name: 'type',
            type: 'string',
            required: false,
            defaultValue: 'text',
            description: 'Input type',
          },
          { name: 'placeholder', type: 'string', required: false, description: 'Placeholder text' },
          { name: 'value', type: 'string', required: false, description: 'Input value' },
          { name: 'onChange', type: 'function', required: false, description: 'Change handler' },
          { name: 'error', type: 'string', required: false, description: 'Error message' },
        ],
      },
      Card: {
        category: 'display',
        description: 'Container component for grouping related content',
        props: [
          { name: 'title', type: 'string', required: false, description: 'Card title' },
          { name: 'children', type: 'ReactNode', required: true, description: 'Card content' },
          {
            name: 'elevated',
            type: 'boolean',
            required: false,
            defaultValue: false,
            description: 'Elevated style',
          },
        ],
      },
      Modal: {
        category: 'overlay',
        description: 'Modal dialog for displaying content over the page',
        props: [
          { name: 'isOpen', type: 'boolean', required: true, description: 'Open state' },
          { name: 'onClose', type: 'function', required: true, description: 'Close handler' },
          { name: 'title', type: 'string', required: false, description: 'Modal title' },
          { name: 'children', type: 'ReactNode', required: true, description: 'Modal content' },
        ],
      },
      Badge: {
        category: 'display',
        description: 'Small label for status or count indicators',
        props: [
          {
            name: 'variant',
            type: 'string',
            required: false,
            defaultValue: 'default',
            description: 'Badge variant',
          },
          { name: 'children', type: 'ReactNode', required: true, description: 'Badge content' },
        ],
      },
    };

    return componentNames.map((name) => ({
      name,
      category: (defaultComponents[name]?.category as any) || 'display',
      description: defaultComponents[name]?.description || `${name} component`,
      props: defaultComponents[name]?.props || [],
      accessibility: {
        keyboardNavigation: true,
      },
    }));
  }

  /**
   * Get default component set
   */
  private getDefaultComponents(): string[] {
    return ['Button', 'Input', 'Card', 'Modal', 'Badge'];
  }

  /**
   * Scaffold the component library to disk
   */
  private async scaffoldLibrary(library: ComponentLibrary): Promise<void> {
    const outputPath = designSystemBuilderConfig.outputPath;
    await this.componentScaffolder.scaffoldLibrary(library, outputPath);
    logger.info(`Library scaffolded to: ${outputPath}`);
  }

  /**
   * Generate a single component
   */
  async generateComponent(
    componentName: string,
    framework: ComponentLibrary['framework'],
    options?: {
      description?: string;
      category?: Component['category'];
    },
  ): Promise<Component> {
    // For now, return a default component structure
    // AI integration can be enabled when properly configured
    const defaultComponent: Component = {
      name: componentName,
      category: options?.category || 'display',
      description: options?.description || `${componentName} component`,
      props: [
        { name: 'children', type: 'ReactNode', required: false, description: 'Component content' },
        {
          name: 'className',
          type: 'string',
          required: false,
          description: 'Additional CSS classes',
        },
      ],
      accessibility: {
        keyboardNavigation: true,
      },
    };

    return defaultComponent;
  }

  /**
   * Generate style guide documentation
   */
  async generateStyleGuide(library: ComponentLibrary): Promise<string> {
    // Generate a basic style guide
    const styleGuide = `# ${library.name} Design System

## Overview

${library.styleGuide?.brandGuidelines || 'A comprehensive design system component library.'}

## Design Tokens

### Colors

The design system includes a comprehensive color palette:

${library.designTokens.colors
  .slice(0, 10)
  .map(
    (color) => `- **${color.name}**: \`${color.value}\` - ${color.description || color.category}`,
  )
  .join('\n')}

### Typography

${library.designTokens.typography
  .slice(0, 5)
  .map((typo) => `- **${typo.name}**: ${typo.fontSize} / ${typo.lineHeight}`)
  .join('\n')}

### Spacing

${library.designTokens.spacing
  .slice(0, 5)
  .map((space) => `- **${space.name}**: \`${space.value}\``)
  .join('\n')}

## Components

${library.components
  .map(
    (component) => `
### ${component.name}

${component.description}

**Category**: ${component.category}

**Props**:
${component.props
  .map(
    (prop) =>
      `- \`${prop.name}\`${prop.required ? ' (required)' : ''}: ${prop.type} - ${prop.description}`,
  )
  .join('\n')}
`,
  )
  .join('\n')}

## Best Practices

1. **Use Design Tokens**: Always reference design tokens instead of hard-coded values
2. **Component Composition**: Build complex components from simpler ones
3. **Accessibility**: Follow WCAG 2.1 AA guidelines
4. **Documentation**: Document all component props and usage examples
5. **Consistency**: Maintain consistent naming and API patterns

## Usage

\`\`\`${library.framework === 'react' ? 'jsx' : library.framework}
import { Button } from '${library.name.toLowerCase().replace(/\s+/g, '-')}';

<Button variant="primary">Click me</Button>
\`\`\`
`;

    return styleGuide;
  }
}
