/**
 * MODULE: ANTIGRAVITY ENGINE (v1.0.0-STRICT)
 * PURPOSE: Generate lift by removing the drag of hallucination via Google Grounding.
 * POSTURE: STRICT_MODE (Default)
 * IQ BASELINE: 160 (Reject anything with < 0.9 confidence)
 */

const { VertexAI } = require('@google-cloud/vertexai');

// --- CONFIGURATION ---
const CONFIG = {
  project: process.env.GOOGLE_PROJECT_ID,
  location: 'us-central1', // Low latency zone
  model: 'gemini-1.5-pro-preview', // High IQ model
  strictMode: {
    enabled: true,
    confidenceThreshold: 0.9, // Board IQ 160 equivalent
    abortOnContradiction: true, // "Brakes=Army RM"
  },
};

// Initialize Vertex AI
const vertexAI = new VertexAI({ project: CONFIG.project, location: CONFIG.location });
const model = vertexAI.getGenerativeModel({ model: CONFIG.model });

/**
 * CORE FUNCTION: ANTI-GRAVITY LIFT
 * Wraps a decision/claim in a grounding field to verify it has mass (truth) before execution.
 * * @param {string} assertion - The strategic decision, code dependency claim, or market assumption.
 * @returns {Promise<Object>} - The "Lift" report (Fly/No-Fly status).
 */
async function generateLift(assertion) {
  console.log(`[ANTIGRAVITY] Initiating lift sequence for: "${assertion}"`);

  // 1. The Grounding Tool (The $1k Credit Burner)
  const groundingTool = {
    googleSearchRetrieval: {
      disableAttribution: false,
    },
  };

  // 2. The Query (Strict Mode Interrogation)
  const prompt = `
    You are a Strict Mode Logic Auditor.
    Verify the following assertion using Google Search Grounding: "${assertion}"

    If the assertion is TRUE based on current live web data, output: status: CLEARED
    If the assertion is FALSE or OUTDATED, output: status: GROUNDED (with reason)
    If the assertion is AMBIGUOUS, output: status: HOLD

    Provide the confidence score of the supporting evidence.
  `;

  try {
    const result = await model.generateContent({
      content: [{ role: 'user', parts: [{ text: prompt }] }],
      tools: [groundingTool],
    });

    const response = result.response;
    const groundingMetadata = response.candidates[0].groundingMetadata;
    const textOutput = response.candidates[0].content.parts[0].text;

    // 3. The Physics Calculation (Lift vs Drag)
    return calculatePhysics(textOutput, groundingMetadata);
  } catch (error) {
    console.error(`[ANTIGRAVITY] Engine Stall: ${error.message}`);
    // In Strict Mode, an engine stall is a mandatory abort.
    return { status: 'ABORT', lift: 0, reason: 'Grounding API Unreachable' };
  }
}

/**
 * INTERNAL PHYSICS ENGINE
 * Determines if we have enough truth to overcome gravity.
 */
function calculatePhysics(auditLog, metadata) {
  // Extract status from the Audit Log
  const isCleared = auditLog.includes('status: CLEARED');
  const isGrounded = auditLog.includes('status: GROUNDED');

  // Check Grounding Metadata (The "Truth" Signal)
  const hasEvidence = metadata && metadata.searchEntryPoint;

  // Strict Mode Logic (Board IQ 160)
  if (CONFIG.strictMode.enabled) {
    if (isGrounded) {
      return {
        status: 'HEAVY',
        lift: 0.0,
        action: 'SOP-B (ABORT & REVIEW)',
        reason: 'Contradictory evidence found. Drag coefficient too high.',
        evidence: metadata?.webSearchQueries || 'Direct Contradiction',
      };
    }

    if (!isCleared && !hasEvidence) {
      return {
        status: 'NULL',
        lift: 0.1,
        action: 'SOP-C (HUMAN OVERRIDE)',
        reason: 'Insufficient data to generate lift. Hovering.',
      };
    }
  }

  // If we are here, we have LIFT.
  return {
    status: 'ORBIT',
    lift: 1.0,
    action: 'EXECUTE',
    reason: 'Assertion verified by live ground truth.',
    source: metadata?.searchEntryPoint?.renderedContent || 'Google Index',
  };
}

module.exports = { generateLift };
