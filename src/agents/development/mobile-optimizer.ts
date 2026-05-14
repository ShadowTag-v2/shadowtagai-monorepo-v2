/**
 * Mobile Optimizer Agent
 * Makes web apps feel native on mobile devices
 */

import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class MobileOptimizerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "mobile-optimizer",
    name: "Mobile Optimizer",
    category: "development",
    description:
      "Makes your web app feel native on phones. Adds offline support, PWA features, touch gestures.",
    tagline: "Mobile-first optimization and PWA implementation",
    capabilities: ["implementation", "optimization"],
    tags: ["mobile", "pwa", "responsive", "offline", "performance"],
    difficulty: "intermediate",
    estimatedTime: "2-4 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Mobile Optimizer specializing in mobile web and Progressive Web Apps.

Your expertise:
1. Responsive design and mobile-first layouts
2. Progressive Web App (PWA) implementation
3. Offline functionality (Service Workers, IndexedDB)
4. Touch gestures and mobile interactions
5. Mobile performance optimization

Focus on:
- Touch-friendly UI (44px+ touch targets)
- Fast mobile performance (< 3s load time)
- Offline support and caching strategies
- App-like experience (no address bar, splash screens)
- Native features (camera, geolocation, notifications)
- Responsive images and lazy loading

Make web apps indistinguishable from native apps.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Write", "Edit"],
    optional: ["Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Mobile Audit",
        description: "Audit mobile experience and performance",
        action: "Analyze responsiveness, touch targets, performance",
      },
      {
        name: "PWA Setup",
        description: "Implement PWA capabilities",
        action: "Add manifest, service worker, icons",
      },
      {
        name: "Offline Support",
        description: "Add offline functionality",
        action: "Implement caching strategies",
      },
      {
        name: "Touch Optimization",
        description: "Optimize for touch interactions",
        action: "Add gestures, improve touch targets",
      },
      {
        name: "Performance",
        description: "Optimize mobile performance",
        action: "Lazy load, optimize images, reduce bundle size",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    _context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
