import { v4 as uuidv4 } from 'uuid';
import { userResearcherAgent } from '../agents/userResearcher';
import type {
  AnalysisRequest,
  FlowAnalysisResult,
  PainPoint,
  UserFeedback,
  UserFlowEvent,
  UserSession,
  UXRecommendation,
} from '../models/schemas';

export class UserResearchService {
  // In-memory storage (replace with database in production)
  private sessions: Map<string, UserSession> = new Map();
  private painPoints: Map<string, PainPoint> = new Map();
  private recommendations: Map<string, UXRecommendation> = new Map();
  private feedbacks: Map<string, UserFeedback> = new Map();
  private analysisResults: Map<string, FlowAnalysisResult> = new Map();

  // Session Management
  async createSession(userId?: string): Promise<UserSession> {
    const session: UserSession = {
      id: uuidv4(),
      userId,
      startTime: new Date(),
      events: [],
    };

    this.sessions.set(session.id, session);
    return session;
  }

  async trackEvent(sessionId: string, event: Omit<UserFlowEvent, 'id'>): Promise<UserFlowEvent> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    const fullEvent: UserFlowEvent = {
      id: uuidv4(),
      ...event,
    };

    session.events.push(fullEvent);
    this.sessions.set(sessionId, session);

    return fullEvent;
  }

  async endSession(sessionId: string, completedGoal?: boolean): Promise<UserSession> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    session.endTime = new Date();
    session.completedGoal = completedGoal;

    if (session.events.length > 0) {
      session.exitPoint = session.events[session.events.length - 1].page;
    }

    this.sessions.set(sessionId, session);
    return session;
  }

  async getSession(sessionId: string): Promise<UserSession | undefined> {
    return this.sessions.get(sessionId);
  }

  async getSessions(filter?: {
    userId?: string;
    startDate?: Date;
    endDate?: Date;
  }): Promise<UserSession[]> {
    let sessions = Array.from(this.sessions.values());

    if (filter?.userId) {
      sessions = sessions.filter((s) => s.userId === filter.userId);
    }

    if (filter?.startDate) {
      sessions = sessions.filter((s) => s.startTime >= filter.startDate!);
    }

    if (filter?.endDate) {
      sessions = sessions.filter((s) => s.startTime <= filter.endDate!);
    }

    return sessions;
  }

  // Pain Point Detection
  async detectPainPoints(sessions?: UserSession[]): Promise<PainPoint[]> {
    const sessionsToAnalyze = sessions || Array.from(this.sessions.values());

    if (sessionsToAnalyze.length === 0) {
      return [];
    }

    // Use the agent to analyze and detect pain points
    const { painPoints, insights } = await userResearcherAgent.analyzeUserFlows(sessionsToAnalyze);

    // Store the pain points
    painPoints.forEach((pp) => {
      this.painPoints.set(pp.id, pp);
    });

    console.log('Pain Point Detection Insights:', insights);

    return painPoints;
  }

  async getRageQuitAnalysis(): Promise<any> {
    const sessions = Array.from(this.sessions.values());
    return await userResearcherAgent.detectRageQuitPoints(sessions);
  }

  // Recommendations
  async generateRecommendations(painPointIds?: string[]): Promise<UXRecommendation[]> {
    let painPoints: PainPoint[];

    if (painPointIds) {
      painPoints = painPointIds
        .map((id) => this.painPoints.get(id))
        .filter((pp) => pp !== undefined) as PainPoint[];
    } else {
      painPoints = Array.from(this.painPoints.values());
    }

    if (painPoints.length === 0) {
      // First detect pain points if none exist
      painPoints = await this.detectPainPoints();
    }

    const recommendations = await userResearcherAgent.generateRecommendations(painPoints);

    // Store recommendations
    recommendations.forEach((rec) => {
      this.recommendations.set(rec.id, rec);
    });

    return recommendations;
  }

  async getRecommendations(filter?: {
    priority?: 'low' | 'medium' | 'high' | 'critical';
    category?: string;
  }): Promise<UXRecommendation[]> {
    let recommendations = Array.from(this.recommendations.values());

    if (filter?.priority) {
      recommendations = recommendations.filter((r) => r.priority === filter.priority);
    }

    if (filter?.category) {
      recommendations = recommendations.filter((r) => r.category === filter.category);
    }

    return recommendations;
  }

  // Flow Analysis
  async analyzeFlow(request?: AnalysisRequest): Promise<FlowAnalysisResult> {
    const now = new Date();
    const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    const timeRange = request?.timeRange || {
      start: dayAgo,
      end: now,
    };

    let sessions = await this.getSessions({
      startDate: timeRange.start,
      endDate: timeRange.end,
    });

    if (request?.pages && request.pages.length > 0) {
      sessions = sessions.filter((session) =>
        session.events.some((event) => request.pages!.includes(event.page)),
      );
    }

    if (request?.userIds && request.userIds.length > 0) {
      sessions = sessions.filter(
        (session) => session.userId && request.userIds!.includes(session.userId),
      );
    }

    // Calculate metrics
    const totalSessions = sessions.length;
    const uniqueUsers = new Set(sessions.map((s) => s.userId).filter(Boolean)).size;
    const completedSessions = sessions.filter((s) => s.completedGoal).length;

    const sessionDurations = sessions
      .filter((s) => s.endTime)
      .map((s) => {
        return s.endTime!.getTime() - s.startTime.getTime();
      });

    const averageSessionDuration =
      sessionDurations.length > 0
        ? sessionDurations.reduce((a, b) => a + b, 0) / sessionDurations.length
        : 0;

    const completionRate = totalSessions > 0 ? completedSessions / totalSessions : 0;
    const dropOffRate = 1 - completionRate;

    // Find most common path
    const paths = sessions.map((s) => s.events.map((e) => e.page).join(' → '));
    const pathCounts = paths.reduce(
      (acc, path) => {
        acc[path] = (acc[path] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );

    const mostCommonPath =
      Object.entries(pathCounts)
        .sort(([, a], [, b]) => b - a)[0]?.[0]
        ?.split(' → ') || [];

    // Find exit pages
    const exitCounts = sessions.reduce(
      (acc, session) => {
        if (session.exitPoint) {
          acc[session.exitPoint] = (acc[session.exitPoint] || 0) + 1;
        }
        return acc;
      },
      {} as Record<string, number>,
    );

    const exitPages = Object.entries(exitCounts)
      .map(([page, count]) => ({
        page,
        count,
        percentage: (count / totalSessions) * 100,
      }))
      .sort((a, b) => b.count - a.count);

    // Detect pain points
    const painPoints = await this.detectPainPoints(sessions);

    // Generate recommendations if requested
    const recommendations = request?.includeRecommendations
      ? await this.generateRecommendations()
      : [];

    const result: FlowAnalysisResult = {
      id: uuidv4(),
      analyzedAt: new Date(),
      timeRange,
      totalSessions,
      totalUsers: uniqueUsers,
      flowMetrics: {
        averageSessionDuration,
        completionRate,
        dropOffRate,
        mostCommonPath,
        exitPages,
      },
      painPoints,
      recommendations,
    };

    this.analysisResults.set(result.id, result);
    return result;
  }

  async optimizeFlow(currentFlow: string[], goalPage: string): Promise<any> {
    const sessions = Array.from(this.sessions.values());
    return await userResearcherAgent.optimizeUserFlow(currentFlow, goalPage, sessions);
  }

  // Feedback Management
  async submitFeedback(feedback: Omit<UserFeedback, 'id' | 'createdAt'>): Promise<UserFeedback> {
    const fullFeedback: UserFeedback = {
      id: uuidv4(),
      createdAt: new Date(),
      ...feedback,
    };

    this.feedbacks.set(fullFeedback.id, fullFeedback);
    return fullFeedback;
  }

  async getFeedback(filter?: {
    type?: string;
    page?: string;
    sentiment?: string;
  }): Promise<UserFeedback[]> {
    let feedbacks = Array.from(this.feedbacks.values());

    if (filter?.type) {
      feedbacks = feedbacks.filter((f) => f.type === filter.type);
    }

    if (filter?.page) {
      feedbacks = feedbacks.filter((f) => f.page === filter.page);
    }

    if (filter?.sentiment) {
      feedbacks = feedbacks.filter((f) => f.sentiment === filter.sentiment);
    }

    return feedbacks;
  }

  async analyzeFeedback(): Promise<any> {
    const feedbacks = Array.from(this.feedbacks.values());
    return await userResearcherAgent.analyzeFeedback(feedbacks);
  }

  // Analytics & Reporting
  async getAnalytics(): Promise<{
    totalSessions: number;
    activeSessions: number;
    totalUsers: number;
    totalPainPoints: number;
    criticalPainPoints: number;
    totalRecommendations: number;
    totalFeedback: number;
  }> {
    const sessions = Array.from(this.sessions.values());
    const painPoints = Array.from(this.painPoints.values());
    const recommendations = Array.from(this.recommendations.values());
    const feedbacks = Array.from(this.feedbacks.values());

    return {
      totalSessions: sessions.length,
      activeSessions: sessions.filter((s) => !s.endTime).length,
      totalUsers: new Set(sessions.map((s) => s.userId).filter(Boolean)).size,
      totalPainPoints: painPoints.length,
      criticalPainPoints: painPoints.filter((pp) => pp.severity === 'critical').length,
      totalRecommendations: recommendations.length,
      totalFeedback: feedbacks.length,
    };
  }

  // Utility methods for data management
  clearAllData(): void {
    this.sessions.clear();
    this.painPoints.clear();
    this.recommendations.clear();
    this.feedbacks.clear();
    this.analysisResults.clear();
  }
}

export const userResearchService = new UserResearchService();
