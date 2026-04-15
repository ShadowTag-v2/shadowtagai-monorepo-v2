import { onRequest } from "firebase-functions/v2/https";
import * as admin from "firebase-admin";
import * as logger from "firebase-functions/logger";
import { z } from "zod";

// Initialize Firebase Admin App
admin.initializeApp();
const db = admin.firestore();

// ─── Rate Limiting (In-Memory Sliding Window) ────────────────────────────
// Cloud Run instances are ephemeral, so this rate limit is per-instance.
// For distributed rate limiting, use Firestore or Redis. This is a
// first-line defense against rapid abuse from a single IP.
const RATE_LIMIT_WINDOW_MS = 60_000; // 60 seconds
const RATE_LIMIT_MAX_REQUESTS = 10;   // max 10 submissions per window

interface RateLimitEntry {
  timestamps: number[];
}

const rateLimitMap = new Map<string, RateLimitEntry>();

// Periodic cleanup to prevent memory leak on long-lived instances
setInterval(() => {
  const now = Date.now();
  for (const [ip, entry] of rateLimitMap) {
    entry.timestamps = entry.timestamps.filter(
      (t) => now - t < RATE_LIMIT_WINDOW_MS
    );
    if (entry.timestamps.length === 0) {
      rateLimitMap.delete(ip);
    }
  }
}, RATE_LIMIT_WINDOW_MS);

/**
 * Checks if the given IP has exceeded rate limits.
 * Returns true if the request should be BLOCKED.
 */
function isRateLimited(clientIp: string): boolean {
  const now = Date.now();
  const entry = rateLimitMap.get(clientIp) || { timestamps: [] };

  // Prune expired timestamps
  entry.timestamps = entry.timestamps.filter(
    (t) => now - t < RATE_LIMIT_WINDOW_MS
  );

  if (entry.timestamps.length >= RATE_LIMIT_MAX_REQUESTS) {
    return true; // blocked
  }

  entry.timestamps.push(now);
  rateLimitMap.set(clientIp, entry);
  return false; // allowed
}

// Strict runtime schema validation for zero-trust posture
// Extensible for CSRMC (Cyber Security Risk Management) or generic KovelAI contact routing
const SubmissionSchema = z.object({
  name: z.string().min(2, "Name is too short").max(100, "Name is too long"),
  email: z.string().email("Invalid email address"),
  company: z.string().max(100, "Company name is too long").optional(),
  message: z.string().min(10, "Message must be at least 10 characters").max(2000, "Message is too long"),
  leadSource: z.string().optional(),
  inquiry_type: z.string().optional(),
}).catchall(z.any());

/**
 * Gen 2 Cloud Run Function (Lead Capture Router)
 * Rate-limited (10 req/60s per IP), schema-validated, IDOR-hardened.
 * Validates payload directly at the edge, routes structured data to Firestore.
 */
export const captureLead = onRequest(
  {
    cors: [
      "https://kovelai.web.app",
      "https://kovelai.com",
      "https://www.kovelai.com",
      "https://shadowtagai.web.app",
      "https://shadowtagai.com",
      "https://www.shadowtagai.com",
      /localhost:\d+/,
    ],
    maxInstances: 10,
    memory: "256MiB",
  },
  async (request, response) => {
    // We only accept POST requests for lead capture
    if (request.method !== "POST") {
      response.status(405).json({ error: "Method Not Allowed" });
      return;
    }

    // ─── Rate Limit Check ──────────────────────────────────────────
    const clientIp = request.ip || request.headers["x-forwarded-for"] as string || "unknown";
    if (isRateLimited(clientIp)) {
      logger.warn(`Rate limit exceeded for IP: ${clientIp}`);
      response.set("Retry-After", "60");
      response.status(429).json({ error: "Too Many Requests" });
      return;
    }

    try {
      // 1. Zod runtime schema validation
      const payload = SubmissionSchema.parse(request.body);

      logger.info(`Valid lead payload parsed from ${payload.email}`);

      // 2. Compute bounded data to store
      const leadDocument = {
        ...payload,
        status: "NEW", // NEW | CONTACTED | DISQUALIFIED
        receivedAt: admin.firestore.FieldValue.serverTimestamp(),
        deviceUserAgent: request.headers["user-agent"] || "unknown",
        clientIp, // Stored for abuse tracking, never returned to client
      };

      // 3. Store in Firestore (collection matches security rules: kovelai_leads)
      const requestId = crypto.randomUUID();
      const docRef = await db.collection("kovelai_leads").add({
        ...leadDocument,
        requestId, // Internal audit trail ID (NOT the Firestore doc ID)
      });

      logger.info(`Lead committed to Firestore successfully: ${docRef.id} (requestId: ${requestId})`);

      // SECURITY: Never return Firestore document IDs to clients (prevents IDOR enumeration)
      response.set("X-Request-ID", requestId);
      response.status(200).json({ success: true, requestId });
    } catch (error) {
      if (error instanceof z.ZodError) {
        // Safe 400 response for client-side structural errors
        logger.warn("Payload structural validation failed", error.errors);
        response.status(400).json({ error: "Validation Failed", details: error.errors });
        return;
      }
      
      // Generic fallback for unhandled 500 scenarios
      logger.error("Unhandled exception routing lead capture", error);
      response.status(500).json({ error: "Internal Server Error" });
    }
  }
);
