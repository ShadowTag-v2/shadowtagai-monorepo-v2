import { type Request, type Response, Router } from 'express';
import { DesignSystemBuilder } from '../agents/design-system-builder';
import { vertexWorkbenchConfig } from '../config/agent-config';
import { VertexWorkbenchIntegration } from '../services/vertex-workbench-integration';
import { DesignSystemRequestSchema } from '../types/design-system';
import { AppError, asyncHandler } from '../utils/error-handler';
import { logger } from '../utils/logger';

const router = Router();
const designSystemBuilder = new DesignSystemBuilder();

// Initialize Vertex AI integration if configured
let vertexIntegration: VertexWorkbenchIntegration | null = null;
if (vertexWorkbenchConfig.projectId) {
  vertexIntegration = new VertexWorkbenchIntegration(vertexWorkbenchConfig);
}

/**
 * POST /api/design-system/create
 * Create a complete design system
 */
router.post(
  '/create',
  asyncHandler(async (req: Request, res: Response) => {
    // Validate request
    const validatedRequest = DesignSystemRequestSchema.parse(req.body);

    logger.info(`Creating design system: ${validatedRequest.projectName}`);

    // Create design system
    const library = await designSystemBuilder.createDesignSystem(validatedRequest);

    res.status(201).json({
      success: true,
      message: 'Design system created successfully',
      data: library,
    });
  }),
);

/**
 * POST /api/design-system/component
 * Generate a single component
 */
router.post(
  '/component',
  asyncHandler(async (req: Request, res: Response) => {
    const { name, framework, description, category } = req.body;

    if (!name || !framework) {
      throw new AppError(400, 'Component name and framework are required');
    }

    const component = await designSystemBuilder.generateComponent(name, framework, {
      description,
      category,
    });

    res.status(201).json({
      success: true,
      message: 'Component generated successfully',
      data: component,
    });
  }),
);

/**
 * POST /api/design-system/style-guide
 * Generate style guide documentation
 */
router.post(
  '/style-guide',
  asyncHandler(async (req: Request, res: Response) => {
    const { library } = req.body;

    if (!library) {
      throw new AppError(400, 'Component library data is required');
    }

    const styleGuide = await designSystemBuilder.generateStyleGuide(library);

    res.status(200).json({
      success: true,
      message: 'Style guide generated successfully',
      data: { styleGuide },
    });
  }),
);

/**
 * POST /api/vertex/component-design
 * Generate component design using Vertex AI
 */
router.post(
  '/vertex/component-design',
  asyncHandler(async (req: Request, res: Response) => {
    if (!vertexIntegration) {
      throw new AppError(503, 'Vertex AI integration not configured');
    }

    const { componentName, framework, requirements } = req.body;

    if (!componentName || !framework) {
      throw new AppError(400, 'Component name and framework are required');
    }

    const design = await vertexIntegration.generateComponentDesign(componentName, {
      framework,
      requirements,
    });

    res.status(200).json({
      success: true,
      message: 'Component design generated',
      data: { design },
    });
  }),
);

/**
 * POST /api/vertex/design-tokens
 * Generate design tokens using Vertex AI
 */
router.post(
  '/vertex/design-tokens',
  asyncHandler(async (req: Request, res: Response) => {
    if (!vertexIntegration) {
      throw new AppError(503, 'Vertex AI integration not configured');
    }

    const { brandGuidelines } = req.body;

    const tokens = await vertexIntegration.generateDesignTokens(brandGuidelines || {});

    res.status(200).json({
      success: true,
      message: 'Design tokens generated',
      data: { tokens },
    });
  }),
);

/**
 * POST /api/vertex/analyze
 * Analyze design system for consistency
 */
router.post(
  '/vertex/analyze',
  asyncHandler(async (req: Request, res: Response) => {
    if (!vertexIntegration) {
      throw new AppError(503, 'Vertex AI integration not configured');
    }

    const { components } = req.body;

    if (!components || !Array.isArray(components)) {
      throw new AppError(400, 'Components array is required');
    }

    const analysis = await vertexIntegration.analyzeDesignSystem(components);

    res.status(200).json({
      success: true,
      message: 'Design system analyzed',
      data: analysis,
    });
  }),
);

/**
 * GET /api/vertex/health
 * Check Vertex AI integration health
 */
router.get(
  '/vertex/health',
  asyncHandler(async (req: Request, res: Response) => {
    if (!vertexIntegration) {
      return res.status(503).json({
        success: false,
        message: 'Vertex AI integration not configured',
      });
    }

    const isHealthy = await vertexIntegration.healthCheck();

    res.status(isHealthy ? 200 : 503).json({
      success: isHealthy,
      message: isHealthy ? 'Vertex AI is healthy' : 'Vertex AI health check failed',
    });
  }),
);

export default router;
