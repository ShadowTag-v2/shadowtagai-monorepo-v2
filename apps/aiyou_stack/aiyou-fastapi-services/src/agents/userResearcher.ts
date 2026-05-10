import { query } from '@anthropic-ai/claude-agent-sdk';
import {
  FlowAnalysisResult,
  type PainPoint,
  type UserSession,
  type UXRecommendation,
} from '../models/schemas';

export class UserResearcherAgent {
  private systemPrompt = `You are a UX research expert who identifies and fixes user pain points.

Your expertise includes:
- Analyzing user flow data to identify bottlenecks and friction points
- Detecting patterns of user frustration (rage clicks, form abandonment, dead ends)
- Identifying where users "rage quit" in the application
- Providing actionable UX improvement recommendations
- Prioritizing fixes based on impact and effort
- Suggesting specific code changes and design improvements

You analyze actual user behavior data and provide concrete, implementable solutions.`;

  async analyzeUserFlows(sessions: UserSession[]): Promise<{
    painPoints: PainPoint[];
    insights: string[];
  }> {
    const sessionsData = JSON.stringify(sessions, null, 2);

    const prompt = `Analyze these user sessions and identify pain points:

${sessionsData}

For each pain point found:
1. Classify the type (rage_click, dead_end, form_abandonment, etc.)
2. Assess severity (low, medium, high, critical)
3. Count affected users and frequency
4. Provide a clear description

Also provide high-level insights about user behavior patterns.

Return your analysis in JSON format with two keys:
- "painPoints": array of pain points with structure matching PainPointSchema
- "insights": array of string insights`;

    try {
      const result = query({
        prompt,
        options: {
          systemPrompt: this.systemPrompt,
          model: 'claude-sonnet-4-5-20250929',
        },
      });

      // Collect the response from the async generator
      let responseText = '';
      for await (const message of result) {
        if (message.type === 'assistant' && 'content' in message) {
          const content = message.content;
          if (Array.isArray(content)) {
            for (const block of content) {
              if (block.type === 'text') {
                responseText += block.text;
              }
            }
          }
        }
      }

      // Parse the response
      const analysis = this.parseAnalysisResponse(responseText);
      return analysis;
    } catch (error) {
      console.error('Error analyzing user flows:', error);
      throw new Error('Failed to analyze user flows');
    }
  }

  async detectRageQuitPoints(sessions: UserSession[]): Promise<{
    rageQuitPages: Array<{ page: string; count: number; percentage: number }>;
    analysis: string;
  }> {
    const exitEvents = sessions.map((session) => {
      const lastEvent = session.events[session.events.length - 1];
      return {
        page: lastEvent?.page || session.exitPoint || 'unknown',
        completedGoal: session.completedGoal,
        sessionDuration:
          session.endTime && session.startTime
            ? new Date(session.endTime).getTime() - new Date(session.startTime).getTime()
            : 0,
      };
    });

    const prompt = `Analyze these exit points to identify rage quit patterns:

${JSON.stringify(exitEvents, null, 2)}

A "rage quit" is when users leave abruptly without completing their goal, often after:
- Very short session durations (< 30 seconds)
- Multiple failed attempts
- Error encounters
- Dead ends

Identify which pages have the highest rage quit rates and explain why.

Return JSON with:
- "rageQuitPages": array of {page, count, percentage}
- "analysis": string explanation`;

    try {
      const result = query({
        prompt,
        options: {
          systemPrompt: this.systemPrompt,
          model: 'claude-sonnet-4-5-20250929',
        },
      });

      let responseText = '';
      for await (const message of result) {
        if (message.type === 'assistant' && 'content' in message) {
          const content = message.content;
          if (Array.isArray(content)) {
            for (const block of content) {
              if (block.type === 'text') {
                responseText += block.text;
              }
            }
          }
        }
      }

      return this.parseRageQuitResponse(responseText);
    } catch (error) {
      console.error('Error detecting rage quit points:', error);
      throw new Error('Failed to detect rage quit points');
    }
  }

  async generateRecommendations(painPoints: PainPoint[]): Promise<UXRecommendation[]> {
    const painPointsData = JSON.stringify(painPoints, null, 2);

    const prompt = `Based on these identified pain points, generate specific, actionable UX improvement recommendations:

${painPointsData}

For each recommendation:
1. Link it to a specific pain point
2. Provide a clear title and description
3. Set priority based on severity and impact
4. Categorize the type of improvement
5. Estimate implementation effort and expected impact
6. Provide concrete implementation steps
7. Suggest specific code changes if applicable
8. Describe the expected outcome

Return a JSON array of recommendations matching the UXRecommendationSchema structure.`;

    try {
      const result = query({
        prompt,
        options: {
          systemPrompt: this.systemPrompt,
          model: 'claude-sonnet-4-5-20250929',
        },
      });

      let responseText = '';
      for await (const message of result) {
        if (message.type === 'assistant' && 'content' in message) {
          const content = message.content;
          if (Array.isArray(content)) {
            for (const block of content) {
              if (block.type === 'text') {
                responseText += block.text;
              }
            }
          }
        }
      }

      return this.parseRecommendationsResponse(responseText);
    } catch (error) {
      console.error('Error generating recommendations:', error);
      throw new Error('Failed to generate recommendations');
    }
  }

  async optimizeUserFlow(
    currentFlow: string[],
    goalPage: string,
    sessions: UserSession[],
  ): Promise<{
    optimizedFlow: string[];
    removedSteps: string[];
    addedSteps: string[];
    rationale: string;
  }> {
    const successfulSessions = sessions.filter((s) => s.completedGoal);
    const failedSessions = sessions.filter((s) => !s.completedGoal);

    const prompt = `Optimize this user flow to reach the goal page:

Current Flow: ${currentFlow.join(' → ')}
Goal Page: ${goalPage}

Successful Sessions (${successfulSessions.length}):
${JSON.stringify(
  successfulSessions.slice(0, 10).map((s) => ({
    pages: s.events.map((e) => e.page),
    duration:
      s.endTime && s.startTime
        ? new Date(s.endTime).getTime() - new Date(s.startTime).getTime()
        : 0,
  })),
  null,
  2,
)}

Failed Sessions (${failedSessions.length}):
${JSON.stringify(
  failedSessions.slice(0, 10).map((s) => ({
    pages: s.events.map((e) => e.page),
    exitPoint: s.exitPoint,
  })),
  null,
  2,
)}

Analyze the data and suggest an optimized flow that:
1. Removes unnecessary steps
2. Adds helpful intermediate steps if needed
3. Reduces friction and confusion
4. Increases completion rate

Return JSON with:
- "optimizedFlow": array of page names in order
- "removedSteps": array of steps removed from current flow
- "addedSteps": array of new steps added
- "rationale": explanation of changes`;

    try {
      const result = query({
        prompt,
        options: {
          systemPrompt: this.systemPrompt,
          model: 'claude-sonnet-4-5-20250929',
        },
      });

      let responseText = '';
      for await (const message of result) {
        if (message.type === 'assistant' && 'content' in message) {
          const content = message.content;
          if (Array.isArray(content)) {
            for (const block of content) {
              if (block.type === 'text') {
                responseText += block.text;
              }
            }
          }
        }
      }

      return this.parseOptimizationResponse(responseText);
    } catch (error) {
      console.error('Error optimizing user flow:', error);
      throw new Error('Failed to optimize user flow');
    }
  }

  async analyzeFeedback(feedbacks: unknown[]): Promise<{
    themes: Array<{ theme: string; count: number; sentiment: string }>;
    priorityIssues: string[];
    summary: string;
  }> {
    const feedbackData = JSON.stringify(feedbacks, null, 2);

    const prompt = `Analyze this user feedback to identify common themes and priority issues:

${feedbackData}

Identify:
1. Common themes and patterns in the feedback
2. Priority issues that need immediate attention
3. Overall sentiment and user satisfaction trends

Return JSON with:
- "themes": array of {theme, count, sentiment}
- "priorityIssues": array of issue descriptions
- "summary": overall analysis summary`;

    try {
      const result = query({
        prompt,
        options: {
          systemPrompt: this.systemPrompt,
          model: 'claude-sonnet-4-5-20250929',
        },
      });

      let responseText = '';
      for await (const message of result) {
        if (message.type === 'assistant' && 'content' in message) {
          const content = message.content;
          if (Array.isArray(content)) {
            for (const block of content) {
              if (block.type === 'text') {
                responseText += block.text;
              }
            }
          }
        }
      }

      return this.parseFeedbackAnalysis(responseText);
    } catch (error) {
      console.error('Error analyzing feedback:', error);
      throw new Error('Failed to analyze feedback');
    }
  }

  // Helper methods to parse responses
  private parseAnalysisResponse(response: string): { painPoints: PainPoint[]; insights: string[] } {
    try {
      // Extract JSON from response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return { painPoints: [], insights: [] };
    } catch (error) {
      console.error('Error parsing analysis response:', error);
      return { painPoints: [], insights: [] };
    }
  }

  private parseRageQuitResponse(response: string): unknown {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return { rageQuitPages: [], analysis: '' };
    } catch (error) {
      console.error('Error parsing rage quit response:', error);
      return { rageQuitPages: [], analysis: '' };
    }
  }

  private parseRecommendationsResponse(response: string): UXRecommendation[] {
    try {
      const jsonMatch = response.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return [];
    } catch (error) {
      console.error('Error parsing recommendations response:', error);
      return [];
    }
  }

  private parseOptimizationResponse(response: string): unknown {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return { optimizedFlow: [], removedSteps: [], addedSteps: [], rationale: '' };
    } catch (error) {
      console.error('Error parsing optimization response:', error);
      return { optimizedFlow: [], removedSteps: [], addedSteps: [], rationale: '' };
    }
  }

  private parseFeedbackAnalysis(response: string): unknown {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return { themes: [], priorityIssues: [], summary: '' };
    } catch (error) {
      console.error('Error parsing feedback analysis:', error);
      return { themes: [], priorityIssues: [], summary: '' };
    }
  }
}

export const userResearcherAgent = new UserResearcherAgent();
