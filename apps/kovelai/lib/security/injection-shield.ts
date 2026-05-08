/**
 * Injection Shield — Indirect Prompt Injection Sanitizer
 *
 * The "Confused Deputy" defense. When the Agent ingests payloads from
 * Google Drive API or Cloud Browser scrapes, adversarial instructions
 * (white-on-white text, invisible Unicode, markdown injection) are
 * neutralized before the payload reaches the LLM context window.
 *
 * This is the READ PROTECTION layer of the Antigravity MCP Gateway.
 */

/** Known adversarial injection patterns */
const INJECTION_PATTERNS: Array<{ pattern: RegExp; name: string }> = [
  // Invisible Unicode characters used to hide instructions
  { pattern: /[\u200B-\u200F\u2028-\u202F\uFEFF\u00AD]/g, name: 'invisible_unicode' },
  // Zero-width joiners/non-joiners embedding hidden text
  { pattern: /[\u200C\u200D]+/g, name: 'zero_width_joiner' },
  // CSS color tricks (white-on-white, font-size:0)
  { pattern: /color\s*:\s*(white|#fff|#ffffff|rgba?\(\s*255/gi, name: 'css_hiding' },
  { pattern: /font-size\s*:\s*0/gi, name: 'font_size_zero' },
  { pattern: /display\s*:\s*none/gi, name: 'display_none' },
  // Direct instruction injection attempts
  {
    pattern: /ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|context)/gi,
    name: 'direct_override',
  },
  { pattern: /system\s*:\s*/gi, name: 'system_prompt_injection' },
  { pattern: /\[INST\]/gi, name: 'inst_tag_injection' },
  { pattern: /<\|im_start\|>/gi, name: 'chatml_injection' },
  // Markdown-based injection (hidden links, images with alt-text instructions)
  { pattern: /!\[.*?(ignore|execute|run|system).*?\]\(.*?\)/gi, name: 'markdown_image_injection' },
  // Base64 encoded payloads that might contain instructions
  { pattern: /data:text\/[^;]+;base64,/gi, name: 'base64_text_payload' },
];

/** Structural delimiters that attackers use to frame fake system prompts */
const STRUCTURAL_DELIMITERS = [
  '---',
  '***',
  '===',
  '```',
  '<system>',
  '</system>',
  '<instructions>',
  '</instructions>',
];

export interface SanitizationResult {
  cleanText: string;
  detectedThreats: Array<{
    patternName: string;
    matchCount: number;
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  }>;
  wasSanitized: boolean;
  threatScore: number; // 0-100
}

/**
 * Sanitizes raw text from external sources against adversarial prompt injections.
 *
 * Strategy:
 * 1. Strip invisible Unicode characters
 * 2. Neutralize CSS/HTML hiding techniques
 * 3. Detect and defang direct instruction overrides
 * 4. Remove structural delimiters that fake system prompts
 * 5. Normalize whitespace to expose hidden content
 */
export function sanitizePromptInjection(rawText: string): SanitizationResult {
  const detectedThreats: SanitizationResult['detectedThreats'] = [];
  let cleanText = rawText;
  let threatScore = 0;

  // Pass 1: Detect and strip injection patterns
  for (const { pattern, name } of INJECTION_PATTERNS) {
    const matches = cleanText.match(pattern);
    if (matches && matches.length > 0) {
      const severity = getSeverity(name);
      detectedThreats.push({
        patternName: name,
        matchCount: matches.length,
        severity,
      });
      threatScore += severityToScore(severity) * matches.length;
      cleanText = cleanText.replace(pattern, '');
    }
  }

  // Pass 2: Strip HTML tags that could hide content
  cleanText = cleanText.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
  cleanText = cleanText.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
  cleanText = cleanText.replace(/<[^>]+>/g, ' ');

  // Pass 3: Defang structural delimiters in suspicious contexts
  for (const delimiter of STRUCTURAL_DELIMITERS) {
    const delimRegex = new RegExp(escapeRegex(delimiter), 'g');
    const matches = cleanText.match(delimRegex);
    if (matches && matches.length > 4) {
      // Excessive delimiters suggest fake system prompt framing
      detectedThreats.push({
        patternName: `structural_delimiter:${delimiter}`,
        matchCount: matches.length,
        severity: 'MEDIUM',
      });
      threatScore += 5;
    }
  }

  // Pass 4: Normalize whitespace (collapses hidden spaces)
  cleanText = cleanText.replace(/\s+/g, ' ').trim();

  // Cap threat score at 100
  threatScore = Math.min(threatScore, 100);

  return {
    cleanText,
    detectedThreats,
    wasSanitized: detectedThreats.length > 0,
    threatScore,
  };
}

/**
 * Hard rejection gate — if threat score exceeds threshold,
 * the payload is quarantined entirely.
 */
export function shouldQuarantine(result: SanitizationResult): boolean {
  return result.threatScore >= 60 || result.detectedThreats.some((t) => t.severity === 'CRITICAL');
}

function getSeverity(patternName: string): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' {
  const severityMap: Record<string, 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'> = {
    invisible_unicode: 'LOW',
    zero_width_joiner: 'LOW',
    css_hiding: 'MEDIUM',
    font_size_zero: 'MEDIUM',
    display_none: 'MEDIUM',
    direct_override: 'CRITICAL',
    system_prompt_injection: 'CRITICAL',
    inst_tag_injection: 'HIGH',
    chatml_injection: 'HIGH',
    markdown_image_injection: 'HIGH',
    base64_text_payload: 'MEDIUM',
  };
  return severityMap[patternName] ?? 'MEDIUM';
}

function severityToScore(severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'): number {
  const scores = { LOW: 2, MEDIUM: 5, HIGH: 15, CRITICAL: 30 };
  return scores[severity];
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
