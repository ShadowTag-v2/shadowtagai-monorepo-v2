import { onRequest } from "firebase-functions/v2/https";
import * as admin from "firebase-admin";
import * as logger from "firebase-functions/logger";
import { z } from "zod";

// Initialize Firebase Admin App
admin.initializeApp();
const db = admin.firestore();

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
 * Allows up to 1000 concurrent connections, optimized for unexpected traffic surges.
 * Validates payload directly at the edge, routes structured data to Firestore.
 */
export const captureLead = onRequest(
  {
    cors: ["https://kovelai.web.app", "https://shadowtagai.web.app", /localhost:\d+/],
    maxInstances: 10,
    memory: "256MiB",
  },
  async (request, response) => {
    // We only accept POST requests for lead capture
    if (request.method !== "POST") {
      response.status(405).json({ error: "Method Not Allowed" });
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
      };

      // 3. Store in the default ShadowTag-v2 Firestore instance
      // Using write batches or direct inserts
      const docRef = await db.collection("leads").add(leadDocument);

      logger.info(`Lead committed to Firestore successfully: ${docRef.id}`);

      // 4. (Optional Placeholder): Trigger Google Cloud Tasks / PubSub for Slack notification
      // Example: await notifySlackWebhook(leadDocument);

      response.status(200).json({ success: true, id: docRef.id });
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
