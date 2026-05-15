import { AnalysisRequestSchema, UserFeedbackSchema, UserFlowEventSchema } from '../models/schemas';
import { userResearchService } from '../services/userResearchService';

export interface RouteRequest<T = any> {
  body?: T;
  params?: Record<string, string>;
  query?: Record<string, string>;
}

export interface RouteResponse<T = any> {
  status: number;
  data?: T;
  error?: string;
}

export class UserResearchRoutes {
  // Session Management Routes
  async createSession(req: RouteRequest): Promise<RouteResponse> {
    try {
      const { userId } = req.body || {};
      const session = await userResearchService.createSession(userId);
      return { status: 201, data: session };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  async trackEvent(req: RouteRequest): Promise<RouteResponse> {
    try {
      const { sessionId } = req.params || {};
      if (!sessionId) {
        return { status: 400, error: 'Session ID is required' };
      }

      const event = UserFlowEventSchema.omit({ id: true }).parse(req.body);
      const trackedEvent = await userResearchService.trackEvent(sessionId, event);
      return { status: 201, data: trackedEvent };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  async endSession(req: RouteRequest): Promise<RouteResponse> {
    try {
      const { sessionId } = req.params || {};
      if (!sessionId) {
        return { status: 400, error: 'Session ID is required' };
      }

      const { completedGoal } = req.body || {};
      const session = await userResearchService.endSession(sessionId, completedGoal);
      return { status: 200, data: session };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  async getSession(req: RouteRequest): Promise<RouteResponse> {
    try {
      const { sessionId } = req.params || {};
      if (!sessionId) {
        return { status: 400, error: 'Session ID is required' };
      }

      const session = await userResearchService.getSession(sessionId);
      if (!session) {
        return { status: 404, error: 'Session not found' };
      }
      return { status: 200, data: session };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  async getSessions(req: RouteRequest): Promise<RouteResponse> {
    try {
      const { userId, startDate, endDate } = req.query || {};
      const sessions = await userResearchService.getSessions({
        userId,
        startDate: startDate ? new Date(startDate) : undefined,
        endDate: endDate ? new Date(endDate) : undefined,
      });
      return { status: 200, data: sessions };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  // Pain Point Detection Routes
  async detectPainPoints(req: RouteRequest): Promise<RouteResponse> {
    try {
      const painPoints = await userResearchService.detectPainPoints();
      return { status: 200, data: painPoints };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  async getRageQuitAnalysis(req: RouteRequest): Promise<RouteResponse> {
    try {
      const analysis = await userResearchService.getRageQuitAnalysis();
      return { status: 200, data: analysis };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  // Recommendations Routes
  async generateRecommendations(req: RouteRequest): Promise<RouteResponse> {
    try {
      const { painPointIds } = req.body || {};
      const recommendations = await userResearchService.generateRecommendations(painPointIds);
      return { status: 200, data: recommendations };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  async getRecommendations(req: RouteRequest): Promise<RouteResponse> {
    try {
      const { priority, category } = req.query || {};
      const recommendations = await userResearchService.getRecommendations({
        priority: priority as any,
        category,
      });
      return { status: 200, data: recommendations };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  // Flow Analysis Routes
  async analyzeFlow(req: RouteRequest): Promise<RouteResponse> {
    try {
      const request = req.body ? AnalysisRequestSchema.parse(req.body) : undefined;
      const analysis = await userResearchService.analyzeFlow(request);
      return { status: 200, data: analysis };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  async optimizeFlow(req: RouteRequest): Promise<RouteResponse> {
    try {
      const { currentFlow, goalPage } = req.body || {};
      if (!currentFlow || !goalPage) {
        return { status: 400, error: 'currentFlow and goalPage are required' };
      }

      const optimization = await userResearchService.optimizeFlow(currentFlow, goalPage);
      return { status: 200, data: optimization };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  // Feedback Routes
  async submitFeedback(req: RouteRequest): Promise<RouteResponse> {
    try {
      const feedback = UserFeedbackSchema.omit({ id: true, createdAt: true }).parse(req.body);
      const savedFeedback = await userResearchService.submitFeedback(feedback);
      return { status: 201, data: savedFeedback };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  async getFeedback(req: RouteRequest): Promise<RouteResponse> {
    try {
      const { type, page, sentiment } = req.query || {};
      const feedbacks = await userResearchService.getFeedback({ type, page, sentiment });
      return { status: 200, data: feedbacks };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  async analyzeFeedback(req: RouteRequest): Promise<RouteResponse> {
    try {
      const analysis = await userResearchService.analyzeFeedback();
      return { status: 200, data: analysis };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  // Analytics Routes
  async getAnalytics(req: RouteRequest): Promise<RouteResponse> {
    try {
      const analytics = await userResearchService.getAnalytics();
      return { status: 200, data: analytics };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }

  // Utility Routes
  async clearAllData(req: RouteRequest): Promise<RouteResponse> {
    try {
      userResearchService.clearAllData();
      return { status: 200, data: { message: 'All data cleared successfully' } };
    } catch (error: unknown) {
      return { status: 500, error: error.message };
    }
  }
}

export const userResearchRoutes = new UserResearchRoutes();

// Route definitions for easy integration
export const routes = {
  // Session Management
  'POST /api/sessions': (req: RouteRequest) => userResearchRoutes.createSession(req),
  'POST /api/sessions/:sessionId/events': (req: RouteRequest) => userResearchRoutes.trackEvent(req),
  'POST /api/sessions/:sessionId/end': (req: RouteRequest) => userResearchRoutes.endSession(req),
  'GET /api/sessions/:sessionId': (req: RouteRequest) => userResearchRoutes.getSession(req),
  'GET /api/sessions': (req: RouteRequest) => userResearchRoutes.getSessions(req),

  // Pain Point Detection
  'POST /api/analysis/pain-points': (req: RouteRequest) => userResearchRoutes.detectPainPoints(req),
  'GET /api/analysis/rage-quits': (req: RouteRequest) =>
    userResearchRoutes.getRageQuitAnalysis(req),

  // Recommendations
  'POST /api/recommendations': (req: RouteRequest) =>
    userResearchRoutes.generateRecommendations(req),
  'GET /api/recommendations': (req: RouteRequest) => userResearchRoutes.getRecommendations(req),

  // Flow Analysis
  'POST /api/analysis/flow': (req: RouteRequest) => userResearchRoutes.analyzeFlow(req),
  'POST /api/analysis/optimize-flow': (req: RouteRequest) => userResearchRoutes.optimizeFlow(req),

  // Feedback
  'POST /api/feedback': (req: RouteRequest) => userResearchRoutes.submitFeedback(req),
  'GET /api/feedback': (req: RouteRequest) => userResearchRoutes.getFeedback(req),
  'POST /api/analysis/feedback': (req: RouteRequest) => userResearchRoutes.analyzeFeedback(req),

  // Analytics
  'GET /api/analytics': (req: RouteRequest) => userResearchRoutes.getAnalytics(req),

  // Utility
  'DELETE /api/data': (req: RouteRequest) => userResearchRoutes.clearAllData(req),
};
