import * as fs from "fs/promises";
import * as path from "path";
import type { Component, ComponentLibrary } from "../types/design-system";

export class ComponentScaffolder {
  /**
   * Generate component code for different frameworks
   */
  async generateComponent(
    component: Component,
    framework: ComponentLibrary["framework"],
    outputPath: string,
  ): Promise<void> {
    switch (framework) {
      case "react":
        await this.generateReactComponent(component, outputPath);
        break;
      case "vue":
        await this.generateVueComponent(component, outputPath);
        break;
      case "svelte":
        await this.generateSvelteComponent(component, outputPath);
        break;
      case "web-components":
        await this.generateWebComponent(component, outputPath);
        break;
      default:
        throw new Error(`Framework ${framework} not supported`);
    }
  }

  /**
   * Generate React component with TypeScript
   */
  private async generateReactComponent(component: Component, outputPath: string): Promise<void> {
    const componentDir = path.join(outputPath, "components", component.name);
    await fs.mkdir(componentDir, { recursive: true });

    // Generate component interface
    const interfaceCode = this.generateReactInterface(component);

    // Generate component code
    const componentCode = `import React from 'react';
import styles from './${component.name}.module.css';

${interfaceCode}

/**
 * ${component.description}
 */
export const ${component.name}: React.FC<${component.name}Props> = ({
${component.props.map((prop) => `  ${prop.name}${!prop.required ? "?" : ""},`).join("\n")}
}) => {
  return (
    <div className={styles.${component.name.toLowerCase()}}>
      {/* Component implementation */}
    </div>
  );
};

${component.name}.displayName = '${component.name}';
`;

    // Generate styles
    const stylesCode = `.${component.name.toLowerCase()} {
  /* Add your styles here */
}
`;

    // Generate tests
    const testCode = `import { render, screen } from '@testing-library/react';
import { ${component.name} } from './${component.name}';

describe('${component.name}', () => {
  it('renders correctly', () => {
    render(<${component.name} />);
    // Add your tests here
  });
});
`;

    // Write files
    await fs.writeFile(path.join(componentDir, `${component.name}.tsx`), componentCode);
    await fs.writeFile(path.join(componentDir, `${component.name}.module.css`), stylesCode);
    await fs.writeFile(path.join(componentDir, `${component.name}.test.tsx`), testCode);
    await this.generateComponentIndex(component, componentDir);
  }

  /**
   * Generate TypeScript interface for React component
   */
  private generateReactInterface(component: Component): string {
    const propsInterface = component.props
      .map((prop) => {
        const optional = prop.required ? "" : "?";
        const description = prop.description ? `  /** ${prop.description} */\n` : "";
        return `${description}  ${prop.name}${optional}: ${prop.type};`;
      })
      .join("\n");

    return `export interface ${component.name}Props {
${propsInterface}
}`;
  }

  /**
   * Generate Vue component (SFC)
   */
  private async generateVueComponent(component: Component, outputPath: string): Promise<void> {
    const componentDir = path.join(outputPath, "components", component.name);
    await fs.mkdir(componentDir, { recursive: true });

    const propsDefinition = component.props
      .map((prop) => {
        return `    ${prop.name}: {
      type: ${this.mapTypeToVue(prop.type)},
      required: ${prop.required},
      ${prop.defaultValue ? `default: ${JSON.stringify(prop.defaultValue)},` : ""}
    },`;
      })
      .join("\n");

    const componentCode = `<template>
  <div class="${component.name.toLowerCase()}">
    <!-- Component template -->
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: '${component.name}',
  props: {
${propsDefinition}
  },
  setup(props) {
    return {};
  },
});
</script>

<style scoped>
.${component.name.toLowerCase()} {
  /* Add your styles here */
}
</style>
`;

    await fs.writeFile(path.join(componentDir, `${component.name}.vue`), componentCode);
  }

  /**
   * Generate Svelte component
   */
  private async generateSvelteComponent(component: Component, outputPath: string): Promise<void> {
    const componentDir = path.join(outputPath, "components", component.name);
    await fs.mkdir(componentDir, { recursive: true });

    const propsDeclaration = component.props
      .map((prop) => {
        const defaultVal = prop.defaultValue ? ` = ${JSON.stringify(prop.defaultValue)}` : "";
        return `  export let ${prop.name}${!prop.required ? "?" : ""}: ${prop.type}${defaultVal};`;
      })
      .join("\n");

    const componentCode = `<script lang="ts">
${propsDeclaration}
</script>

<div class="${component.name.toLowerCase()}">
  <!-- Component template -->
</div>

<style>
  .${component.name.toLowerCase()} {
    /* Add your styles here */
  }
</style>
`;

    await fs.writeFile(path.join(componentDir, `${component.name}.svelte`), componentCode);
  }

  /**
   * Generate Web Component
   */
  private async generateWebComponent(component: Component, outputPath: string): Promise<void> {
    const componentDir = path.join(outputPath, "components", component.name);
    await fs.mkdir(componentDir, { recursive: true });

    const observedAttributes = component.props.map((p) => `'${p.name.toLowerCase()}'`).join(", ");

    const componentCode = `class ${component.name} extends HTMLElement {
  static get observedAttributes() {
    return [${observedAttributes}];
  }

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  render() {
    if (!this.shadowRoot) return;

    this.shadowRoot.innerHTML = \`
      <style>
        :host {
          display: block;
        }
      </style>
      <div class="${component.name.toLowerCase()}">
        <!-- Component template -->
      </div>
    \`;
  }
}

customElements.define('${this.toKebabCase(component.name)}', ${component.name});
`;

    await fs.writeFile(path.join(componentDir, `${component.name}.ts`), componentCode);
  }

  /**
   * Generate index file for component
   */
  private async generateComponentIndex(component: Component, componentDir: string): Promise<void> {
    const indexCode = `export { ${component.name} } from './${component.name}';
export type { ${component.name}Props } from './${component.name}';
`;
    await fs.writeFile(path.join(componentDir, "index.ts"), indexCode);
  }

  /**
   * Scaffold entire component library structure
   */
  async scaffoldLibrary(library: ComponentLibrary, outputPath: string): Promise<void> {
    // Create directory structure
    await fs.mkdir(path.join(outputPath, "components"), { recursive: true });
    await fs.mkdir(path.join(outputPath, "tokens"), { recursive: true });
    await fs.mkdir(path.join(outputPath, "styles"), { recursive: true });
    await fs.mkdir(path.join(outputPath, "utils"), { recursive: true });

    // Generate design tokens
    await this.generateDesignTokensFile(library.designTokens, outputPath);

    // Generate components
    for (const component of library.components) {
      await this.generateComponent(component, library.framework, outputPath);
    }

    // Generate package.json
    await this.generatePackageJson(library, outputPath);

    // Generate README
    await this.generateReadme(library, outputPath);

    // Generate main index file
    await this.generateMainIndex(library, outputPath);
  }

  /**
   * Generate design tokens as CSS variables and TypeScript
   */
  private async generateDesignTokensFile(tokens: unknown, outputPath: string): Promise<void> {
    const tokensDir = path.join(outputPath, "tokens");

    // Generate CSS variables
    const cssVariables = this.generateCSSVariables(tokens);
    await fs.writeFile(path.join(tokensDir, "tokens.css"), cssVariables);

    // Generate TypeScript tokens
    const tsTokens = `export const designTokens = ${JSON.stringify(tokens, null, 2)} as const;

export type DesignTokens = typeof designTokens;
`;
    await fs.writeFile(path.join(tokensDir, "tokens.ts"), tsTokens);
  }

  /**
   * Generate CSS variables from design tokens
   */
  private generateCSSVariables(tokens: unknown): string {
    let css = ":root {\n";

    // Colors
    if (tokens.colors) {
      tokens.colors.forEach((color: unknown) => {
        css += `  --color-${color.name}: ${color.value};\n`;
      });
    }

    // Typography
    if (tokens.typography) {
      tokens.typography.forEach((typo: unknown) => {
        css += `  --font-size-${typo.name}: ${typo.fontSize};\n`;
        css += `  --font-weight-${typo.name}: ${typo.fontWeight};\n`;
        css += `  --line-height-${typo.name}: ${typo.lineHeight};\n`;
      });
    }

    // Spacing
    if (tokens.spacing) {
      tokens.spacing.forEach((space: unknown) => {
        css += `  --spacing-${space.name}: ${space.value};\n`;
      });
    }

    // Border radius
    if (tokens.borderRadius) {
      Object.entries(tokens.borderRadius).forEach(([key, value]) => {
        css += `  --radius-${key}: ${value};\n`;
      });
    }

    // Shadows
    if (tokens.shadows) {
      Object.entries(tokens.shadows).forEach(([key, value]) => {
        css += `  --shadow-${key}: ${value};\n`;
      });
    }

    css += "}\n";
    return css;
  }

  /**
   * Generate package.json for the component library
   */
  private async generatePackageJson(library: ComponentLibrary, outputPath: string): Promise<void> {
    const packageJson = {
      name: library.name.toLowerCase().replace(/\s+/g, "-"),
      version: library.version,
      description: `${library.name} Design System Component Library`,
      main: "dist/index.js",
      types: "dist/index.d.ts",
      scripts: {
        build: "tsc",
        dev: "tsc --watch",
        test: "jest",
      },
      peerDependencies: this.getPeerDependencies(library.framework),
      devDependencies: this.getDevDependencies(library.framework),
    };

    await fs.writeFile(path.join(outputPath, "package.json"), JSON.stringify(packageJson, null, 2));
  }

  /**
   * Generate README for the component library
   */
  private async generateReadme(library: ComponentLibrary, outputPath: string): Promise<void> {
    const readme = `# ${library.name}

${library.styleGuide?.brandGuidelines || "A comprehensive design system component library."}

## Installation

\`\`\`bash
npm install ${library.name.toLowerCase().replace(/\s+/g, "-")}
\`\`\`

## Usage

\`\`\`${library.framework === "react" ? "jsx" : library.framework}
import { Button } from '${library.name.toLowerCase().replace(/\s+/g, "-")}';

// Use the component
<Button variant="primary">Click me</Button>
\`\`\`

## Components

${library.components.map((c) => `- **${c.name}**: ${c.description}`).join("\n")}

## Design Tokens

This library uses a comprehensive design token system for consistency:

- Colors
- Typography
- Spacing
- Border Radius
- Shadows
- Breakpoints

## Documentation

For detailed documentation, please visit our [documentation site](#).

## License

MIT
`;

    await fs.writeFile(path.join(outputPath, "README.md"), readme);
  }

  /**
   * Generate main index file
   */
  private async generateMainIndex(library: ComponentLibrary, outputPath: string): Promise<void> {
    const exports = library.components
      .map((c) => `export { ${c.name} } from './components/${c.name}';`)
      .join("\n");

    const indexCode = `${exports}

export { designTokens } from './tokens/tokens';
export type { DesignTokens } from './tokens/tokens';
`;

    await fs.writeFile(path.join(outputPath, "index.ts"), indexCode);
  }

  /**
   * Helper methods
   */
  private mapTypeToVue(type: string): string {
    const typeMap: Record<string, string> = {
      string: "String",
      number: "Number",
      boolean: "Boolean",
      array: "Array",
      object: "Object",
    };
    return typeMap[type.toLowerCase()] || "Object";
  }

  private toKebabCase(str: string): string {
    return str.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase();
  }

  private getPeerDependencies(framework: string): Record<string, string> {
    const deps: Record<string, Record<string, string>> = {
      react: { react: "^18.0.0", "react-dom": "^18.0.0" },
      vue: { vue: "^3.0.0" },
      svelte: { svelte: "^4.0.0" },
      angular: { "@angular/core": "^17.0.0" },
      "web-components": {},
    };
    return deps[framework] || {};
  }

  private getDevDependencies(framework: string): Record<string, string> {
    const common = {
      typescript: "^5.0.0",
      "@types/node": "^20.0.0",
    };

    const frameworkDeps: Record<string, Record<string, string>> = {
      react: {
        ...common,
        "@types/react": "^18.0.0",
        "@types/react-dom": "^18.0.0",
      },
      vue: {
        ...common,
        "@vitejs/plugin-vue": "^4.0.0",
      },
      svelte: {
        ...common,
        "@sveltejs/kit": "^2.0.0",
      },
    };

    return frameworkDeps[framework] || common;
  }
}
