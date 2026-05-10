/**
 * Intent classification system
 * Determines whether to THINK, BUILD, or SCALE
 */

import { AnthropicVertex } from '@anthropic-ai/vertex-sdk';
import { INTENT_CLASSIFIER_PROMPT } from '../prompts/system-prompts';
import { type IntentClassification, Mode } from '../types';
import { logger } from '../utils/logger';

export class IntentClassifier {
  private client: AnthropicVertex;

  constructor() {
    this.client = new AnthropicVertex({
      region: process.env.CLOUD_ML_REGION || 'us-central1',
      projectId: process.env.ANTHROPIC_VERTEX_PROJECT_ID,
    });
  }

  /**
   * Classify user intent and determine the appropriate mode
   */
  async classify(userInput: string): Promise<IntentClassification> {
    try {
      logger.info('Classifying intent', { inputLength: userInput.length });

      const response = await this.client.messages.create({
        model: 'claude-opus-4-1@20250805',
        max_tokens: 500,
        temperature: 0, // Deterministic classification
        system: INTENT_CLASSIFIER_PROMPT,
        messages: [
          {
            role: 'user',
            content: [{ type: 'text', text: userInput }],
          },
        ],
      });

      const responseText = response.content[0].text;
      const classification = this.parseClassification(responseText);

      logger.info('Intent classified', {
        mode: classification.mode,
        confidence: classification.confidence,
      });

      return classification;
    } catch (error) {
      logger.error('Intent classification failed, defaulting to THINK', {
        error: error instanceof Error ? error.message : String(error),
      });

      // Fallback to THINK mode if classification fails
      return {
        mode: Mode.THINK,
        confidence: 0.5,
        reasoning: 'Classification failed, defaulting to strategic reasoning',
        extractedParams: {},
      };
    }
  }

  /**
   * Parse the JSON response from Claude
   */
  private parseClassification(responseText: string): IntentClassification {
    try {
      // Extract JSON from response (handle markdown code blocks)
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error('No JSON found in response');
      }

      const parsed = JSON.parse(jsonMatch[0]);

      return {
        mode: this.normalizeMode(parsed.mode),
        confidence: parsed.confidence || 0.5,
        reasoning: parsed.reasoning || '',
        extractedParams: parsed.extractedParams || {},
      };
    } catch (error) {
      logger.warn('Failed to parse classification JSON, using heuristics', {
        error: error instanceof Error ? error.message : String(error),
      });

      return this.heuristicClassification(responseText);
    }
  }

  /**
   * Normalize mode string to Mode enum
   */
  private normalizeMode(modeStr: string): Mode {
    const normalized = modeStr.toLowerCase().trim();

    switch (normalized) {
      case 'think':
        return Mode.THINK;
      case 'build':
        return Mode.BUILD;
      case 'scale':
        return Mode.SCALE;
      case 'research':
        return Mode.RESEARCH;
      default:
        logger.warn('Unknown mode, defaulting to THINK', { mode: modeStr });
        return Mode.THINK;
    }
  }

  /**
   * Fallback heuristic classification if JSON parsing fails
   */
  private heuristicClassification(text: string): IntentClassification {
    const lowerText = text.toLowerCase();

    // Research keywords - check first as highest priority for multi-source queries
    const researchKeywords = [
      'research',
      'investigate',
      'deep dive',
      'what do we know',
      'gather information',
      'look into',
      'prior art',
      'competitive analysis',
      'market research',
      'intel',
      'intelligence',
      'summarize from',
    ];
    const researchScore = researchKeywords.filter((kw) => lowerText.includes(kw)).length;

    // Build keywords
    const buildKeywords = [
      'create',
      'build',
      'deploy',
      'implement',
      'make',
      'develop',
      'setup',
      'configure',
    ];
    const buildScore = buildKeywords.filter((kw) => lowerText.includes(kw)).length;

    // Scale keywords
    const scaleKeywords = [
      'scale',
      'grow',
      'optimize',
      'increase',
      'expand',
      'improve',
      'accelerate',
    ];
    const scaleScore = scaleKeywords.filter((kw) => lowerText.includes(kw)).length;

    // Think keywords
    const thinkKeywords = [
      'why',
      'how',
      'should',
      'analyze',
      'evaluate',
      'compare',
      'recommend',
      'strategy',
    ];
    const thinkScore = thinkKeywords.filter((kw) => lowerText.includes(kw)).length;

    let mode: Mode;
    let confidence: number;

    // Research takes priority for multi-source queries
    if (researchScore > 0 && researchScore >= buildScore && researchScore >= scaleScore) {
      mode = Mode.RESEARCH;
      confidence = Math.min(0.7 + researchScore * 0.1, 0.95);
    } else if (buildScore > scaleScore && buildScore > thinkScore) {
      mode = Mode.BUILD;
      confidence = Math.min(0.6 + buildScore * 0.1, 0.9);
    } else if (scaleScore > thinkScore) {
      mode = Mode.SCALE;
      confidence = Math.min(0.6 + scaleScore * 0.1, 0.9);
    } else {
      mode = Mode.THINK;
      confidence = Math.min(0.6 + thinkScore * 0.1, 0.9);
    }

    return {
      mode,
      confidence,
      reasoning: 'Heuristic classification based on keyword matching',
      extractedParams: mode === Mode.RESEARCH ? { sources: ['drive', 'gmail', 'web'] } : {},
    };
  }
}
