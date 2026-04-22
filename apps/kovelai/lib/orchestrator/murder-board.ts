/**
 * @fileoverview Murder Board Orchestrator — 7-Step Cognitive Pipeline
 *
 * Runs the War Room pipeline as a series of Cloud Tasks.
 * Each stage is an independent, retryable task that writes its output
 * to Firestore and enqueues the next stage.
 *
 * Queue: Google Cloud Tasks (doctrine: no Inngest, no BullMQ)
 * Database: Firestore (doctrine: no Supabase)
 * Runtime: Cloud Run (triggers from Cloud Tasks HTTP target)
 *
 * @see WAR_ROOM_ARCHITECTURE.md — Technical design
 * @see legal-prompts.ts — System prompts for each stage
 */

import { initializeApp, cert, getApps, type App } from 'firebase-admin/app';
import { getFirestore, type Firestore, FieldValue } from 'firebase-admin/firestore';
import { google } from '@ai-sdk/google';
import { anthropic } from '@ai-sdk/anthropic';
import { generateText } from 'ai';
import {
  INTAKE_EXTRACTION_PROMPT,
  OSINT_QUERY_GENERATOR_PROMPT,
  VERB_AUDITOR_PROMPT,
  WAR_ROOM_ORACLE_PROMPT,
  CITATION_VALIDATOR_PROMPT,
  BRIEF_BUILDER_PROMPT,
} from '@/lib/prompts/legal-prompts';
import { executePrivilegedWebSearch } from '@/lib/intelligence/vertex_search_engine';
import {
  pushToLawyerVault,
  draftShadowInvoice,
  generateHeppnerReceipt,
} from '@/lib/clio-vault';

// ─── Firebase initialization ─────────────────────────────
let app: App;
if (!getApps().length) {
  app = initializeApp();
} else {
  app = getApps()[0];
}
const db: Firestore = getFirestore(app);

// ─── Types ───────────────────────────────────────────────

/** Pipeline session state stored in Firestore. */
export interface MurderBoardSession {
  sessionId: string;
  firmId: string;
  status: 'intake' | 'osint' | 'verb_audit' | 'oracle' | 'citations' | 'brief' | 'vault' | 'complete' | 'failed';
  startedAt: FirebaseFirestore.Timestamp;
  completedAt?: FirebaseFirestore.Timestamp;
  transcript: string;
  clioOAuthToken?: string;
  contextCacheId?: string;
  seuToken: string;
  // Stage outputs
  intakeData?: IntakeData;
  osintQueries?: string[];
  osintResults?: string;
  verbAudit?: VerbEntry[];
  oracleMemo?: string;
  citations?: CitationEntry[];
  briefContent?: string;
  error?: string;
}

interface IntakeData {
  entities: string[];
  dates: string[];
  locations: string[];
  claims: string[];
  emotional_state: string;
  urgency_flags: string[];
}

export interface VerbEntry {
  verb: string;
  context: string;
  kinematic_classification: string;
  cause_of_action: string;
  element_matched: string;
  confidence: number;
  strengthens_or_weakens: 'strengthens' | 'weakens' | 'neutral';
}

export interface CitationEntry {
  index: number;
  authority: string;
  type: 'statute' | 'case' | 'regulation' | 'rule' | 'secondary';
  citation_format_correct: boolean;
  excerpt: string;
  relevance_score: number;
  status: 'verified' | 'unverified' | 'suspect';
  notes?: string;
}

// ─── Session Management ──────────────────────────────────

/**
 * Create a new Murder Board session in Firestore.
 */
export async function createSession(
  sessionId: string,
  firmId: string,
  transcript: string,
  seuToken: string,
  clioOAuthToken?: string,
  contextCacheId?: string,
): Promise<MurderBoardSession> {
  const session: MurderBoardSession = {
    sessionId,
    firmId,
    status: 'intake',
    startedAt: FieldValue.serverTimestamp() as unknown as FirebaseFirestore.Timestamp,
    transcript,
    clioOAuthToken,
    contextCacheId,
    seuToken,
  };

  await db.collection('murder_board_sessions').doc(sessionId).set(session);
  return session;
}

/**
 * Update session status and stage output.
 */
async function updateSession(
  sessionId: string,
  update: Partial<MurderBoardSession>,
): Promise<void> {
  await db.collection('murder_board_sessions').doc(sessionId).update(update);
}

/**
 * Get the current session state.
 */
export async function getSession(sessionId: string): Promise<MurderBoardSession | null> {
  const doc = await db.collection('murder_board_sessions').doc(sessionId).get();
  return doc.exists ? (doc.data() as MurderBoardSession) : null;
}

// ─── Pipeline Stages ─────────────────────────────────────

/**
 * Stage 1: Intake Extraction
 *
 * Extracts structured entities from the raw client transcript.
 * Uses flash-lite for cost efficiency (prompt repetition applied).
 */
export async function runStage1Intake(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session) throw new Error(`Session ${sessionId} not found`);

  try {
    // arXiv:2512.14982 — duplicate instruction for non-reasoning model accuracy
    const repeatedPrompt = `${INTAKE_EXTRACTION_PROMPT}\n\n[RE-EVALUATE]:\n${INTAKE_EXTRACTION_PROMPT}`;

    const result = await generateText({
      model: google('gemini-2.5-flash-lite-preview'),
      system: repeatedPrompt,
      messages: [{ role: 'user', content: session.transcript }],
    });

    const intakeData: IntakeData = JSON.parse(result.text);

    await updateSession(sessionId, {
      intakeData,
      status: 'osint',
    });
  } catch (error) {
    await updateSession(sessionId, {
      status: 'failed',
      error: `Stage 1 failed: ${error instanceof Error ? error.message : String(error)}`,
    });
    throw error;
  }
}

/**
 * Stage 2: Web OSINT
 *
 * Generates search queries from intake data and executes
 * privileged web search via Vertex AI Enterprise Search.
 */
export async function runStage2Osint(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session?.intakeData) throw new Error(`Session ${sessionId} missing intake data`);

  try {
    // Generate search queries
    const queryGenResult = await generateText({
      model: google('gemini-2.5-flash-lite-preview'),
      system: OSINT_QUERY_GENERATOR_PROMPT,
      messages: [{ role: 'user', content: JSON.stringify(session.intakeData) }],
    });

    const queries: string[] = JSON.parse(queryGenResult.text);

    // Execute privileged search for each query
    const searchResults: string[] = [];
    for (const query of queries.slice(0, 5)) {
      const result = await executePrivilegedWebSearch(query, session.firmId);
      searchResults.push(result);
    }

    const combinedResults = searchResults.join('\n\n---\n\n');

    await updateSession(sessionId, {
      osintQueries: queries,
      osintResults: combinedResults,
      status: 'verb_audit',
    });
  } catch (error) {
    await updateSession(sessionId, {
      status: 'failed',
      error: `Stage 2 failed: ${error instanceof Error ? error.message : String(error)}`,
    });
    throw error;
  }
}

/**
 * Stage 3: Verb Audit (Action Verb Auditor)
 *
 * Analyzes client transcript for kinematic action verbs
 * that map to legal causes of action.
 */
export async function runStage3VerbAudit(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session) throw new Error(`Session ${sessionId} not found`);

  try {
    // arXiv:2512.14982 — repeated instruction for verb classification accuracy
    const repeatedPrompt = `${VERB_AUDITOR_PROMPT}\n\n[CRITICAL RE-EVALUATION]:\n${VERB_AUDITOR_PROMPT}`;

    const result = await generateText({
      model: google('gemini-2.5-flash-lite-preview'),
      system: repeatedPrompt,
      messages: [{ role: 'user', content: session.transcript }],
    });

    const verbs: VerbEntry[] = JSON.parse(result.text);

    // Write to verb_ledger collection for analytics
    await db.collection('verb_ledger').doc(sessionId).set({
      session_id: sessionId,
      firm_id: session.firmId,
      timestamp: FieldValue.serverTimestamp(),
      verbs,
      causes_of_action_summary: summarizeVerbsByAction(verbs),
    });

    await updateSession(sessionId, {
      verbAudit: verbs,
      status: 'oracle',
    });
  } catch (error) {
    await updateSession(sessionId, {
      status: 'failed',
      error: `Stage 3 failed: ${error instanceof Error ? error.message : String(error)}`,
    });
    throw error;
  }
}

/**
 * Stage 4: Oracle Synthesis
 *
 * Full-power multi-model strategy memo generation.
 * Uses Gemini Pro (with Aegaeon cache) or Claude Sonnet fallback.
 */
export async function runStage4Oracle(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session?.intakeData || !session.verbAudit)
    throw new Error(`Session ${sessionId} missing prerequisite data`);

  try {
    const enrichedContext = `
## INTAKE DATA
${JSON.stringify(session.intakeData, null, 2)}

## OSINT RESULTS
${session.osintResults || 'No OSINT results available'}

## VERB AUDIT
${JSON.stringify(session.verbAudit, null, 2)}

## RAW TRANSCRIPT
${session.transcript}
`;

    // Use Aegaeon-cached Gemini Pro if available, else Claude Sonnet 4
    const model = session.contextCacheId
      ? google('gemini-1.5-pro-002')
      : anthropic('claude-sonnet-4-20250514');

    const result = await generateText({
      model,
      system: WAR_ROOM_ORACLE_PROMPT,
      messages: [{ role: 'user', content: enrichedContext }],
    });

    await updateSession(sessionId, {
      oracleMemo: result.text,
      status: 'citations',
    });
  } catch (error) {
    await updateSession(sessionId, {
      status: 'failed',
      error: `Stage 4 failed: ${error instanceof Error ? error.message : String(error)}`,
    });
    throw error;
  }
}

/**
 * Stage 5: Citation Chain Validation
 *
 * Validates all legal citations from the Oracle memo.
 */
export async function runStage5Citations(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session?.oracleMemo) throw new Error(`Session ${sessionId} missing Oracle memo`);

  try {
    const result = await generateText({
      model: google('gemini-2.5-flash-lite-preview'),
      system: CITATION_VALIDATOR_PROMPT,
      messages: [{ role: 'user', content: session.oracleMemo }],
    });

    const citations: CitationEntry[] = JSON.parse(result.text);

    await updateSession(sessionId, {
      citations,
      status: 'brief',
    });
  } catch (error) {
    await updateSession(sessionId, {
      status: 'failed',
      error: `Stage 5 failed: ${error instanceof Error ? error.message : String(error)}`,
    });
    throw error;
  }
}

/**
 * Stage 6: Brief Builder
 *
 * Generates the final Attorney Work-Product brief in markdown
 * (to be converted to PDF by the Python brief_builder service).
 */
export async function runStage6Brief(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session?.oracleMemo || !session?.citations)
    throw new Error(`Session ${sessionId} missing prerequisite data`);

  try {
    const fullContext = `
## ORACLE STRATEGY MEMO
${session.oracleMemo}

## VALIDATED CITATIONS
${JSON.stringify(session.citations, null, 2)}

## VERB AUDIT
${JSON.stringify(session.verbAudit, null, 2)}

## INTAKE DATA
${JSON.stringify(session.intakeData, null, 2)}
`;

    const result = await generateText({
      model: anthropic('claude-sonnet-4-20250514'),
      system: BRIEF_BUILDER_PROMPT,
      messages: [{ role: 'user', content: fullContext }],
    });

    await updateSession(sessionId, {
      briefContent: result.text,
      status: 'vault',
    });
  } catch (error) {
    await updateSession(sessionId, {
      status: 'failed',
      error: `Stage 6 failed: ${error instanceof Error ? error.message : String(error)}`,
    });
    throw error;
  }
}

/**
 * Stage 7: Vault Push
 *
 * Pushes all outputs to the lawyer's vault (Clio) and
 * auto-drafts the shadow invoice.
 */
export async function runStage7VaultPush(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session?.briefContent)
    throw new Error(`Session ${sessionId} missing brief content`);

  try {
    if (session.clioOAuthToken) {
      // Push Oracle memo + brief to Clio vault
      const heppnerReceipt = generateHeppnerReceipt(session.seuToken, session.firmId);

      await pushToLawyerVault(
        session.clioOAuthToken,
        `${session.oracleMemo}\n\n---\n\nBRIEF:\n${session.briefContent}`,
        heppnerReceipt,
      );

      // Auto-draft shadow invoice (War Room session = premium billing)
      await draftShadowInvoice(session.clioOAuthToken, 4.0, 450.0);
    }

    await updateSession(sessionId, {
      status: 'complete',
      completedAt: FieldValue.serverTimestamp() as unknown as FirebaseFirestore.Timestamp,
    });

    // Write to Kovel telemetry
    await db.collection('kovel_telemetry').add({
      firm_id: session.firmId,
      session_id: sessionId,
      pipeline_type: 'war_room',
      stages_completed: 7,
      verb_count: session.verbAudit?.length || 0,
      citation_count: session.citations?.length || 0,
      model_routed: 'gemini-pro + claude-sonnet',
      timestamp: FieldValue.serverTimestamp(),
    });
  } catch (error) {
    await updateSession(sessionId, {
      status: 'failed',
      error: `Stage 7 failed: ${error instanceof Error ? error.message : String(error)}`,
    });
    throw error;
  }
}

// ─── Utilities ───────────────────────────────────────────

/**
 * Summarize verb entries into a causes-of-action overview.
 */
function summarizeVerbsByAction(
  verbs: VerbEntry[],
): Record<string, { count: number; avg_confidence: number }> {
  const summary: Record<string, { total_confidence: number; count: number }> = {};

  for (const verb of verbs) {
    const action = verb.cause_of_action;
    if (!summary[action]) {
      summary[action] = { total_confidence: 0, count: 0 };
    }
    summary[action].count += 1;
    summary[action].total_confidence += verb.confidence;
  }

  const result: Record<string, { count: number; avg_confidence: number }> = {};
  for (const [action, data] of Object.entries(summary)) {
    result[action] = {
      count: data.count,
      avg_confidence: Math.round((data.total_confidence / data.count) * 100) / 100,
    };
  }

  return result;
}

/**
 * Run the full pipeline sequentially.
 * In production, each stage is enqueued as a Cloud Task.
 * This function is for development/testing.
 */
export async function runFullPipeline(sessionId: string): Promise<void> {
  await runStage1Intake(sessionId);
  await runStage2Osint(sessionId);
  await runStage3VerbAudit(sessionId);
  await runStage4Oracle(sessionId);
  await runStage5Citations(sessionId);
  await runStage6Brief(sessionId);
  await runStage7VaultPush(sessionId);
}
