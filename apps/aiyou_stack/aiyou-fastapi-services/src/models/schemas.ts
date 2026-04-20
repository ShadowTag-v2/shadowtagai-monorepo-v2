import { z } from 'zod';

// User Flow Event Schema
export const UserFlowEventSchema = z.object({
  id: z.string().uuid(),
  sessionId: z.string(),
  userId: z.string().optional(),
  timestamp: z.date(),
  eventType: z.enum([
    'page_view',
    'click',
    'form_submit',
    'navigation',
    'error',
    'exit',
    'scroll',
    'input_focus',
    'input_blur',
    'hover',
  ]),
  elementId: z.string().optional(),
  elementType: z.string().optional(),
  page: z.string(),
  previousPage: z.string().optional(),
  metadata: z.record(z.any()).optional(),
  duration: z.number().optional(), // time spent on page/element in ms
});

export type UserFlowEvent = z.infer<typeof UserFlowEventSchema>;

// User Session Schema
export const UserSessionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().optional(),
  startTime: z.date(),
  endTime: z.date().optional(),
  events: z.array(UserFlowEventSchema),
  deviceType: z.enum(['desktop', 'mobile', 'tablet']).optional(),
  browser: z.string().optional(),
  completedGoal: z.boolean().optional(),
  exitPoint: z.string().optional(),
});

export type UserSession = z.infer<typeof UserSessionSchema>;

// Pain Point Schema
export const PainPointSchema = z.object({
  id: z.string().uuid(),
  type: z.enum([
    'rage_click',
    'dead_end',
    'form_abandonment',
    'high_bounce_rate',
    'error_prone',
    'slow_load',
    'confusing_navigation',
    'repeated_attempts',
  ]),
  severity: z.enum(['low', 'medium', 'high', 'critical']),
  page: z.string(),
  elementId: z.string().optional(),
  affectedUsers: z.number(),
  frequency: z.number(),
  description: z.string(),
  detectedAt: z.date(),
  metrics: z
    .object({
      averageTimeSpent: z.number().optional(),
      dropOffRate: z.number().optional(),
      errorRate: z.number().optional(),
      retryCount: z.number().optional(),
    })
    .optional(),
});

export type PainPoint = z.infer<typeof PainPointSchema>;

// UX Improvement Recommendation Schema
export const UXRecommendationSchema = z.object({
  id: z.string().uuid(),
  painPointId: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  priority: z.enum(['low', 'medium', 'high', 'critical']),
  category: z.enum([
    'ui_design',
    'navigation',
    'performance',
    'content',
    'functionality',
    'accessibility',
  ]),
  implementation: z.object({
    effort: z.enum(['low', 'medium', 'high']),
    impact: z.enum(['low', 'medium', 'high']),
    steps: z.array(z.string()),
    codeChanges: z
      .array(
        z.object({
          file: z.string(),
          description: z.string(),
          snippet: z.string().optional(),
        }),
      )
      .optional(),
  }),
  expectedOutcome: z.string(),
  createdAt: z.date(),
});

export type UXRecommendation = z.infer<typeof UXRecommendationSchema>;

// User Feedback Schema
export const UserFeedbackSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().optional(),
  sessionId: z.string().uuid(),
  type: z.enum(['bug_report', 'feature_request', 'usability_issue', 'general']),
  rating: z.number().min(1).max(5).optional(),
  page: z.string(),
  message: z.string(),
  screenshot: z.string().optional(), // base64 or URL
  sentiment: z.enum(['positive', 'neutral', 'negative']).optional(),
  createdAt: z.date(),
  tags: z.array(z.string()).optional(),
});

export type UserFeedback = z.infer<typeof UserFeedbackSchema>;

// Flow Analysis Result Schema
export const FlowAnalysisResultSchema = z.object({
  id: z.string().uuid(),
  analyzedAt: z.date(),
  timeRange: z.object({
    start: z.date(),
    end: z.date(),
  }),
  totalSessions: z.number(),
  totalUsers: z.number(),
  flowMetrics: z.object({
    averageSessionDuration: z.number(),
    completionRate: z.number(),
    dropOffRate: z.number(),
    mostCommonPath: z.array(z.string()),
    exitPages: z.array(
      z.object({
        page: z.string(),
        count: z.number(),
        percentage: z.number(),
      }),
    ),
  }),
  painPoints: z.array(PainPointSchema),
  recommendations: z.array(UXRecommendationSchema),
});

export type FlowAnalysisResult = z.infer<typeof FlowAnalysisResultSchema>;

// Analysis Request Schema
export const AnalysisRequestSchema = z.object({
  timeRange: z
    .object({
      start: z.date(),
      end: z.date(),
    })
    .optional(),
  pages: z.array(z.string()).optional(),
  userIds: z.array(z.string()).optional(),
  includeRecommendations: z.boolean().default(true),
});

export type AnalysisRequest = z.infer<typeof AnalysisRequestSchema>;
