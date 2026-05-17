/**
 * App Check Middleware — Firebase Cloud Functions (Gen 2)
 * ═══════════════════════════════════════════════════════
 *
 * Validates Firebase App Check tokens on incoming requests.
 * Enforces attestation for all client-facing endpoints.
 *
 * Usage:
 *   import { verifyAppCheck } from './appCheckMiddleware';
 *   // In your onRequest handler:
 *   if (!await verifyAppCheck(request, response)) return;
 */

import { getAppCheck } from "firebase-admin/app-check";
import * as logger from "firebase-functions/logger";
import type { Request, Response } from "firebase-functions/v2/https";

/**
 * Verifies the X-Firebase-AppCheck header on the request.
 * Returns true if the token is valid (caller should proceed).
 * Returns false if the token is missing/invalid (response already sent).
 *
 * In development (localhost), bypass is allowed when
 * `process.env.FUNCTIONS_EMULATOR === 'true'`.
 */
export async function verifyAppCheck(request: Request, response: Response): Promise<boolean> {
  // Allow emulator bypass for local development
  if (process.env.FUNCTIONS_EMULATOR === "true") {
    logger.info("App Check bypassed: running in emulator");
    return true;
  }

  const appCheckToken = request.header("X-Firebase-AppCheck");

  if (!appCheckToken) {
    logger.warn("App Check: missing token", {
      ip: request.ip,
      path: request.path,
      userAgent: request.headers["user-agent"],
    });
    response.status(401).json({ error: "Unauthorized: App Check token required" });
    return false;
  }

  try {
    await getAppCheck().verifyToken(appCheckToken);
    return true;
  } catch (error) {
    logger.warn("App Check: invalid token", {
      ip: request.ip,
      path: request.path,
      error: (error as Error).message,
    });
    response.status(401).json({ error: "Unauthorized: invalid App Check token" });
    return false;
  }
}
