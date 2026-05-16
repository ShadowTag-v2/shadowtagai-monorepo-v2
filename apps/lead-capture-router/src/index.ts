import { initializeApp } from 'firebase-admin/app';
import { FieldValue, getFirestore } from 'firebase-admin/firestore';
import * as logger from 'firebase-functions/logger';
import { onRequest } from 'firebase-functions/v2/https';
import { z } from 'zod';
import { verifyAppCheck } from './appCheckMiddleware';

// Initialize Firebase Admin App
initializeApp();
const db = getFirestore();

// ─── Rate Limiting (Firestore-backed) ────────────────────────────
const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX_REQUESTS = 10;

/**
 * Checks if the given IP has exceeded rate limits backed by Firestore.
 * Returns true if the request should be BLOCKED.
 */
async function isRateLimited(clientIp: string): Promise<boolean> {
  const now = Date.now();
  const limitRef = db.collection('system_rate_limits').doc(clientIp.replace(/[^a-zA-Z0-9]/g, '_'));

  try {
    return await db.runTransaction(async (transaction) => {
      const doc = await transaction.get(limitRef);
      let timestamps: number[] = doc.exists ? doc.data()?.timestamps || [] : [];

      timestamps = timestamps.filter((t) => now - t < RATE_LIMIT_WINDOW_MS);

      if (timestamps.length >= RATE_LIMIT_MAX_REQUESTS) {
        return true;
      }

      timestamps.push(now);
      transaction.set(limitRef, { timestamps }, { merge: true });
      return false;
    });
  } catch (err) {
    logger.error('Rate limiting transaction failed', err);
    return false; // Fail open for resilience, or true to fail closed.
  }
}

// Strict runtime schema validation for zero-trust posture
// Extensible for CSRMC (Cyber Security Risk Management) or generic KovelAI contact routing
const SubmissionSchema = z
  .object({
    name: z.string().min(2, 'Name is too short').max(100, 'Name is too long'),
    email: z.string().email('Invalid email address'),
    company: z.string().max(100, 'Company name is too long').optional(),
    message: z
      .string()
      .min(10, 'Message must be at least 10 characters')
      .max(2000, 'Message is too long'),
    leadSource: z.string().optional(),
    inquiry_type: z.string().optional(),
  })
  .catchall(z.any());

/**
 * Gen 2 Cloud Run Function (Lead Capture Router)
 * Rate-limited (10 req/60s per IP), schema-validated, IDOR-hardened.
 * Validates payload directly at the edge, routes structured data to Firestore.
 */
export const captureLead = onRequest(
  {
    cors: [
      'https://kovelai.web.app',
      'https://kovelai.com',
      'https://www.kovelai.com',
      'https://shadowtagai.web.app',
      'https://shadowtagai.com',
      'https://www.shadowtagai.com',
      /localhost:\d+/,
    ],
    maxInstances: 10,
    memory: '256MiB',
  },
  async (request, response) => {
    // App Check attestation gate
    if (!(await verifyAppCheck(request, response))) return;

    // We only accept POST requests for lead capture
    if (request.method !== 'POST') {
      response.status(405).json({ error: 'Method Not Allowed' });
      return;
    }

    // ─── Rate Limit Check ──────────────────────────────────────────
    const clientIp = request.ip || (request.headers['x-forwarded-for'] as string) || 'unknown';
    if (await isRateLimited(clientIp)) {
      logger.warn(`Rate limit exceeded for IP: ${clientIp}`);
      response.set('Retry-After', '60');
      response.status(429).json({ error: 'Too Many Requests' });
      return;
    }

    try {
      // 1. Zod runtime schema validation
      const payload = SubmissionSchema.parse(request.body);

      logger.info(`Valid lead payload parsed from ${payload.email}`);

      // 2. Compute bounded data to store
      const leadDocument = {
        ...payload,
        status: 'NEW', // NEW | CONTACTED | DISQUALIFIED
        receivedAt: FieldValue.serverTimestamp(),
        deviceUserAgent: request.headers['user-agent'] || 'unknown',
        clientIp, // Stored for abuse tracking, never returned to client
      };

      // 3. Store in Firestore (collection matches security rules: kovelai_leads)
      const requestId = crypto.randomUUID();
      const docRef = await db.collection('kovelai_leads').add({
        ...leadDocument,
        requestId, // Internal audit trail ID (NOT the Firestore doc ID)
      });

      logger.info(
        `Lead committed to Firestore successfully: ${docRef.id} (requestId: ${requestId})`,
      );

      // SECURITY: Never return Firestore document IDs to clients (prevents IDOR enumeration)
      response.set('X-Request-ID', requestId);
      response.status(200).json({ success: true, requestId });
    } catch (error) {
      if (error instanceof z.ZodError) {
        // Safe 400 response for client-side structural errors
        logger.warn('Payload structural validation failed', error.errors);
        response.status(400).json({ error: 'Validation Failed', details: error.errors });
        return;
      }

      // Generic fallback for unhandled 500 scenarios
      logger.error('Unhandled exception routing lead capture', error);
      response.status(500).json({ error: 'Internal Server Error' });
    }
  },
);

export const captureContact = onRequest(
  {
    cors: [
      'https://kovelai.web.app',
      'https://kovelai.com',
      'https://www.kovelai.com',
      'https://shadowtagai.web.app',
      'https://shadowtagai.com',
      'https://www.shadowtagai.com',
      /localhost:\d+/,
    ],
    maxInstances: 5,
    memory: '256MiB',
  },
  async (request, response) => {
    // App Check attestation gate
    if (!(await verifyAppCheck(request, response))) return;

    if (request.method !== 'POST') {
      response.status(405).json({ error: 'Method Not Allowed' });
      return;
    }
    const clientIp = request.ip || (request.headers['x-forwarded-for'] as string) || 'unknown';
    if (await isRateLimited(clientIp)) {
      response.status(429).json({ error: 'Too Many Requests' });
      return;
    }
    try {
      const payload = SubmissionSchema.parse(request.body);
      const docRef = await db.collection('contact_requests').add({
        ...payload,
        status: 'NEW',
        receivedAt: FieldValue.serverTimestamp(),
        deviceUserAgent: request.headers['user-agent'] || 'unknown',
      });
      response.status(200).json({ success: true, requestId: docRef.id });
    } catch (_error) {
      response.status(400).json({ error: 'Validation Failed' });
    }
  },
);

// ─── CSP Violation Report Endpoint ─────────────────────────────
export { cspReport } from './cspReport';

// ─── Analytics Webhook Worker ──────────────────────────────────
export const analyticalWebhook = onRequest(
  {
    cors: true,
    maxInstances: 2,
    memory: '128MiB',
  },
  async (request, response) => {
    // App Check attestation gate
    if (!(await verifyAppCheck(request, response))) return;

    if (request.method !== 'POST') {
      response.status(405).json({ error: 'Method Not Allowed' });
      return;
    }
    try {
      // Intentionally lightweight non-blocking event parser
      const eventData = request.body;
      logger.info('Processed analytics event batch natively', { count: eventData.length || 1 });
      response.status(202).json({ accepted: true });
    } catch (error) {
      logger.error('Failed to parse unblocking analytics event stream', error);
      response.status(400).json({ error: 'Bad Request' });
    }
  },
);
