/**
 * @fileoverview The Omniverse Edge Router (arXiv:2512.14982 Implementation)
 *
 * The Core Engine. Hardware RAM only. Validates S.E.U., duplicates prompt
 * for accuracy, executes dual-payload, and drops data.
 *
 * Architecture:
 * ┌─────────────────────────────────────────────────────────┐
 * │  Client Query                                           │
 * │    ↓                                                    │
 * │  S.E.U. Gate (IP + JWT + Payment verification)          │
 * │    ↓                                                    │
 * │  Vertex AI Enterprise Search (ZDR OSINT)                │
 * │    ↓                                                    │
 * │  arXiv:2512.14982 Prompt Repetition                     │
 * │    ↓                                                    │
 * │  ┌──────────────┐    ┌───────────────────────────┐      │
 * │  │ TRACK A      │    │ TRACK B                   │      │
 * │  │ Pacifier     │    │ Oracle                    │      │
 * │  │ (Flash-Lite) │    │ (Gemini Pro / Claude)     │      │
 * │  │ → Client SSE │    │ → Lawyer Vault (Clio)     │      │
 * │  └──────────────┘    └───────────────────────────┘      │
 * │                                                         │
 * │  Cache-Control: no-store (anti-forensic)                │
 * └─────────────────────────────────────────────────────────┘
 *
 * @see PERPLEXITY_PARADIGM.md — Dual-payload architecture
 * @see DIGITAL_PRIVILEGE_SHIELD.md — Kovel attestation
 */

import { anthropic } from '@ai-sdk/anthropic';
import { google } from '@ai-sdk/google';
import { generateText, streamText } from 'ai';
import { NextResponse } from 'next/server';
import { draftShadowInvoice, generateHeppnerReceipt, pushToLawyerVault } from '@/lib/clio-vault';
import { executePrivilegedWebSearch } from '@/lib/intelligence/vertex_search_engine';
import { LAWYER_ORACLE_PROMPT, TRIAGE_PACIFIER_PROMPT } from '@/lib/prompts';
import { verifySeuToken } from '@/lib/security/seu_and_stripe';

export const runtime = 'edge';

interface IntakeRequestBody {
  messages: Array<{ role: string; content: string }>;
  seuToken: string;
  webSearchQuery?: string;
  clioOAuthToken?: string;
  contextCacheId?: string;
}

export async function POST(req: Request) {
  try {
    const {
      messages,
      seuToken,
      webSearchQuery,
      clioOAuthToken,
      contextCacheId,
    }: IntakeRequestBody = await req.json();

    // ──────────────────────────────────────────────────────
    // 1. S.E.U. SECURITY GATE
    // ──────────────────────────────────────────────────────
    const clientIp = req.headers.get('x-forwarded-for') || 'unknown';
    const payload = await verifySeuToken(seuToken, clientIp);

    // ──────────────────────────────────────────────────────
    // 2. WEB-TO-PRIVILEGE PIPELINE (Vertex ZDR Search)
    // ──────────────────────────────────────────────────────
    const searchContext = webSearchQuery
      ? await executePrivilegedWebSearch(webSearchQuery, payload.firmId ?? 'unknown')
      : '';
    const hybridContext = searchContext ? `[WEB OSINT/RESEARCH]:\n${searchContext}` : '';

    // ──────────────────────────────────────────────────────
    // 3. ALGORITHMIC OPTIMIZATION: arXiv:2512.14982
    //    Prompt Repetition for non-reasoning models
    // ──────────────────────────────────────────────────────
    const lastUserQuery = messages[messages.length - 1].content;
    const optimizedPrompt = `${lastUserQuery}\n\n[SYSTEM DIRECTIVE: RE-EVALUATE CONTEXT]\n\n${lastUserQuery}`;
    const optimizedMessages = [
      ...messages.slice(0, -1),
      { role: 'user', content: optimizedPrompt },
    ];

    // ──────────────────────────────────────────────────────
    // 4. TRACK A: Client Pacifier (Fast model → SSE stream)
    // ──────────────────────────────────────────────────────
    const systemMessages = hybridContext
      ? [{ role: 'system' as const, content: hybridContext }]
      : [];

    const pacifierStream = await streamText({
      model: google('gemini-2.5-flash-lite-preview'),
      system: TRIAGE_PACIFIER_PROMPT,
      messages: [...optimizedMessages, ...systemMessages],
    });

    // ──────────────────────────────────────────────────────
    // 5. TRACK B: Lawyer Oracle (Background → Vault)
    //    Runs in the background via waitUntil (Edge Runtime)
    // ──────────────────────────────────────────────────────
    if (clioOAuthToken) {
      // @ts-expect-error: waitUntil is available in Edge Runtime
      req.waitUntil(
        (async () => {
          // Hit Gemini 3.1 Flash Lite using Aegaeon Context Slab (84% cost drop)
          // or fall back to Claude Sonnet 4
          const oracleModel = contextCacheId
            ? google('gemini-3.1-flash-lite-preview', {
                // @ts-expect-error: cached content config
                useCachedContent: contextCacheId,
              })
            : anthropic('claude-sonnet-4-20250514');

          const oracleResponse = await generateText({
            model: oracleModel,
            system: LAWYER_ORACLE_PROMPT,
            messages: [...optimizedMessages, ...systemMessages],
          });

          // Stateless Direct-to-Vault Transfer
          const heppnerReceipt = generateHeppnerReceipt(seuToken, payload.firmId ?? 'unknown');
          await pushToLawyerVault(clioOAuthToken, oracleResponse.text, heppnerReceipt);

          // Auto-Draft Shadow Invoice in Clio
          await draftShadowInvoice(clioOAuthToken, 2.5, 350.0);
        })(),
      );
    }

    // ──────────────────────────────────────────────────────
    // 6. RETURN: SSE stream with anti-forensic headers
    // ──────────────────────────────────────────────────────
    return new NextResponse(pacifierStream.toDataStream(), {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'X-Kovel-Attestation': 'active',
        'X-SEU-Sandbox': payload.sandboxId,
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      {
        error: 'Stateless Execution Failed or S.E.U. Blocked',
        detail: message,
      },
      { status: 403 },
    );
  }
}
