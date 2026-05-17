/**
 * MFA Gate — Attorney Dashboard Access Control
 *
 * Enforces multi-factor authentication for attorney-level dashboard access
 * using Firebase Auth MFA enrollment and verification.
 *
 * Requires: firebase-admin/auth with MFA capabilities
 * Applies to: /dashboard/*, /api/oracle/*, /api/approval/*
 */

import { getAuth } from "firebase-admin/auth";
import type { NextRequest } from "next/server";
import { createLogger } from "../observability/structured-logger";

const logger = createLogger("mfa-gate");
const auth = getAuth();

/** Routes requiring MFA */
const MFA_REQUIRED_ROUTES = [
  "/dashboard",
  "/api/oracle",
  "/api/approval",
  "/api/triage",
  "/api/admin",
];

/** MFA verification result */
interface MFAVerification {
  authenticated: boolean;
  mfaVerified: boolean;
  uid?: string;
  email?: string;
  error?: string;
}

/**
 * Verify that a request has a valid Firebase ID token with MFA factor.
 */
export async function verifyMFA(request: NextRequest): Promise<MFAVerification> {
  const authHeader = request.headers.get("authorization");

  if (!authHeader?.startsWith("Bearer ")) {
    logger.warn("Missing or malformed authorization header", {
      path: request.nextUrl.pathname,
    });
    return { authenticated: false, mfaVerified: false, error: "Missing authorization header" };
  }

  const idToken = authHeader.substring(7);

  try {
    // Verify the ID token
    const decoded = await auth.verifyIdToken(idToken, true);

    // Check if this route requires MFA
    const requiresMFA = MFA_REQUIRED_ROUTES.some((route) =>
      request.nextUrl.pathname.startsWith(route),
    );

    if (!requiresMFA) {
      return {
        authenticated: true,
        mfaVerified: true,
        uid: decoded.uid,
        email: decoded.email,
      };
    }

    // Check for MFA factor in the token
    const hasMFA =
      decoded.firebase?.sign_in_second_factor === "totp" ||
      decoded.firebase?.sign_in_second_factor === "phone";

    if (!hasMFA) {
      logger.warn("MFA required but not present", {
        uid: decoded.uid,
        path: request.nextUrl.pathname,
        signInProvider: decoded.firebase?.sign_in_provider,
      });
      return {
        authenticated: true,
        mfaVerified: false,
        uid: decoded.uid,
        email: decoded.email,
        error: "MFA verification required for this resource",
      };
    }

    logger.info("MFA verification passed", {
      uid: decoded.uid,
      path: request.nextUrl.pathname,
      mfaFactor: decoded.firebase?.sign_in_second_factor,
    });

    return {
      authenticated: true,
      mfaVerified: true,
      uid: decoded.uid,
      email: decoded.email,
    };
  } catch (err) {
    const error = err instanceof Error ? err.message : "Unknown error";
    logger.error("Token verification failed", { error });
    return { authenticated: false, mfaVerified: false, error };
  }
}

/**
 * Enroll TOTP MFA for an attorney user.
 * Returns the TOTP secret for QR code generation.
 */
export async function enrollTOTP(uid: string): Promise<{
  secretKey: string;
  qrCodeUrl: string;
}> {
  // Generate TOTP secret via Firebase Admin
  const totpConfig = await auth.generateTotpMultiFactorSecret(uid, {
    displayName: "KovelAI Attorney Auth",
  });

  logger.info("TOTP enrollment initiated", { uid });

  return {
    secretKey: totpConfig.sharedSecretKey,
    qrCodeUrl: totpConfig.generateQrCodeUrl(
      (await auth.getUser(uid)).email || "attorney@firm.com",
      "KovelAI",
    ),
  };
}

/**
 * Check if a user has MFA enrolled.
 */
export async function hasMFAEnrolled(uid: string): Promise<boolean> {
  const user = await auth.getUser(uid);
  return (user.multiFactor?.enrolledFactors?.length ?? 0) > 0;
}
