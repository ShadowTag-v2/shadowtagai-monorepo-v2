Object.defineProperty(exports, '__esModule', { value: true });
exports.analyticalWebhook =
  exports.cspReport =
  exports.captureContact =
  exports.captureLead =
    void 0;
const app_1 = require('firebase-admin/app');
const firestore_1 = require('firebase-admin/firestore');
const logger = require('firebase-functions/logger');
const https_1 = require('firebase-functions/v2/https');
const zod_1 = require('zod');
// Initialize Firebase Admin App
(0, app_1.initializeApp)();
const db = (0, firestore_1.getFirestore)();
// ─── Rate Limiting (Firestore-backed) ────────────────────────────
const RATE_LIMIT_WINDOW_MS = 60000;
const RATE_LIMIT_MAX_REQUESTS = 10;
/**
 * Checks if the given IP has exceeded rate limits backed by Firestore.
 * Returns true if the request should be BLOCKED.
 */
async function isRateLimited(clientIp) {
  const now = Date.now();
  const limitRef = db.collection('system_rate_limits').doc(clientIp.replace(/[^a-zA-Z0-9]/g, '_'));
  try {
    return await db.runTransaction(async (transaction) => {
      var _a;
      const doc = await transaction.get(limitRef);
      let timestamps = doc.exists
        ? ((_a = doc.data()) === null || _a === void 0 ? void 0 : _a.timestamps) || []
        : [];
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
const SubmissionSchema = zod_1.z
  .object({
    name: zod_1.z.string().min(2, 'Name is too short').max(100, 'Name is too long'),
    email: zod_1.z.string().email('Invalid email address'),
    company: zod_1.z.string().max(100, 'Company name is too long').optional(),
    message: zod_1.z
      .string()
      .min(10, 'Message must be at least 10 characters')
      .max(2000, 'Message is too long'),
    leadSource: zod_1.z.string().optional(),
    inquiry_type: zod_1.z.string().optional(),
  })
  .catchall(zod_1.z.any());
/**
 * Gen 2 Cloud Run Function (Lead Capture Router)
 * Rate-limited (10 req/60s per IP), schema-validated, IDOR-hardened.
 * Validates payload directly at the edge, routes structured data to Firestore.
 */
exports.captureLead = (0, https_1.onRequest)(
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
    // We only accept POST requests for lead capture
    if (request.method !== 'POST') {
      response.status(405).json({ error: 'Method Not Allowed' });
      return;
    }
    // ─── Rate Limit Check ──────────────────────────────────────────
    const clientIp = request.ip || request.headers['x-forwarded-for'] || 'unknown';
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
      const leadDocument = Object.assign(Object.assign({}, payload), {
        status: 'NEW',
        receivedAt: firestore_1.FieldValue.serverTimestamp(),
        deviceUserAgent: request.headers['user-agent'] || 'unknown',
        clientIp,
      });
      // 3. Store in Firestore (collection matches security rules: kovelai_leads)
      const requestId = crypto.randomUUID();
      const docRef = await db
        .collection('kovelai_leads')
        .add(Object.assign(Object.assign({}, leadDocument), { requestId }));
      logger.info(
        `Lead committed to Firestore successfully: ${docRef.id} (requestId: ${requestId})`,
      );
      // SECURITY: Never return Firestore document IDs to clients (prevents IDOR enumeration)
      response.set('X-Request-ID', requestId);
      response.status(200).json({ success: true, requestId });
    } catch (error) {
      if (error instanceof zod_1.z.ZodError) {
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
exports.captureContact = (0, https_1.onRequest)(
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
    if (request.method !== 'POST') {
      response.status(405).json({ error: 'Method Not Allowed' });
      return;
    }
    const clientIp = request.ip || request.headers['x-forwarded-for'] || 'unknown';
    if (await isRateLimited(clientIp)) {
      response.status(429).json({ error: 'Too Many Requests' });
      return;
    }
    try {
      const payload = SubmissionSchema.parse(request.body);
      const docRef = await db.collection('contact_requests').add(
        Object.assign(Object.assign({}, payload), {
          status: 'NEW',
          receivedAt: firestore_1.FieldValue.serverTimestamp(),
          deviceUserAgent: request.headers['user-agent'] || 'unknown',
        }),
      );
      response.status(200).json({ success: true, requestId: docRef.id });
    } catch (_error) {
      response.status(400).json({ error: 'Validation Failed' });
    }
  },
);
// ─── CSP Violation Report Endpoint ─────────────────────────────
var cspReport_1 = require('./cspReport');
Object.defineProperty(exports, 'cspReport', { enumerable: true, get: () => cspReport_1.cspReport });
// ─── Analytics Webhook Worker ──────────────────────────────────
exports.analyticalWebhook = (0, https_1.onRequest)(
  {
    cors: true,
    maxInstances: 2,
    memory: '128MiB',
  },
  async (request, response) => {
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
//# sourceMappingURL=index.js.map
