import { z } from 'zod';

// Design Token Schemas
export const ColorTokenSchema = z.object({
  name: z.string(),
  value: z.string(),
  category: z.enum(['primary', 'secondary', 'neutral', 'semantic', 'extended']),
  description: z.string().optional(),
});

export const TypographyTokenSchema = z.object({
  name: z.string(),
  fontSize: z.string(),
  fontWeight: z.union([z.string(), z.number()]),
  lineHeight: z.string(),
  letterSpacing: z.string().optional(),
  fontFamily: z.string(),
});

export const SpacingTokenSchema = z.object({
  name: z.string(),
  value: z.string(),
  scale: z.number(),
});

export const DesignTokensSchema = z.object({
  colors: z.array(ColorTokenSchema),
  typography: z.array(TypographyTokenSchema),
  spacing: z.array(SpacingTokenSchema),
  borderRadius: z.record(z.string()),
  shadows: z.record(z.string()),
  breakpoints: z.record(z.string()),
});

// Component Schemas
export const ComponentSchema = z.object({
  name: z.string(),
  category: z.enum(['layout', 'input', 'display', 'feedback', 'navigation', 'overlay']),
  description: z.string(),
  props: z.array(
    z.object({
      name: z.string(),
      type: z.string(),
      required: z.boolean(),
      defaultValue: z.any().optional(),
      description: z.string(),
    }),
  ),
  examples: z.array(z.string()).optional(),
  accessibility: z
    .object({
      ariaLabel: z.string().optional(),
      role: z.string().optional(),
      keyboardNavigation: z.boolean(),
    })
    .optional(),
});

export const ComponentLibrarySchema = z.object({
  name: z.string(),
  version: z.string(),
  framework: z.enum(['react', 'vue', 'angular', 'svelte', 'web-components']),
  components: z.array(ComponentSchema),
  designTokens: DesignTokensSchema,
  styleGuide: z
    .object({
      brandGuidelines: z.string().optional(),
      usagePatterns: z.string().optional(),
      bestPractices: z.string().optional(),
    })
    .optional(),
});

// Request/Response Schemas
export const DesignSystemRequestSchema = z.object({
  projectName: z.string(),
  framework: z.enum(['react', 'vue', 'angular', 'svelte', 'web-components']),
  theme: z
    .object({
      primaryColor: z.string().optional(),
      secondaryColor: z.string().optional(),
      fontFamily: z.string().optional(),
    })
    .optional(),
  components: z.array(z.string()).optional(),
  features: z
    .object({
      darkMode: z.boolean().optional(),
      responsive: z.boolean().optional(),
      accessibility: z.boolean().optional(),
      animations: z.boolean().optional(),
    })
    .optional(),
});

export const VertexWorkbenchConfigSchema = z.object({
  projectId: z.string(),
  location: z.string().default('us-central1'),
  modelName: z.string().default('gemini-pro'),
  credentials: z.string().optional(),
});

// Type exports
export type ColorToken = z.infer<typeof ColorTokenSchema>;
export type TypographyToken = z.infer<typeof TypographyTokenSchema>;
export type SpacingToken = z.infer<typeof SpacingTokenSchema>;
export type DesignTokens = z.infer<typeof DesignTokensSchema>;
export type Component = z.infer<typeof ComponentSchema>;
export type ComponentLibrary = z.infer<typeof ComponentLibrarySchema>;
export type DesignSystemRequest = z.infer<typeof DesignSystemRequestSchema>;
export type VertexWorkbenchConfig = z.infer<typeof VertexWorkbenchConfigSchema>;

// Agent Configuration
export interface AgentConfig {
  systemPrompt: string;
  tools: string[];
  maxTokens?: number;
  temperature?: number;
}

export interface DesignSystemBuilderConfig extends AgentConfig {
  defaultFramework: ComponentLibrary['framework'];
  outputPath: string;
  vertexConfig?: VertexWorkbenchConfig;
}
