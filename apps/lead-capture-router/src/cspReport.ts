/**
 * CSP Violation Report Endpoint — Cloud Function (Gen 2)
 * ══════════════════════════════════════════════════════
 *
 * Receives CSP violation reports and logs them to Cloud Logging.
 * Add report-uri or report-to directive to CSP headers pointing to this function.
 *
 * Deployed at: https://us-central1-shadowtag-omega-v4.cloudfunctions.net/cspReport
 */

import { onRequest } from "firebase-functions/v2/https";
import { logger } from "firebase-functions/v2";

interface CSPViolationReport {
  "csp-report"?: {
    "document-uri"?: string;
    "referrer"?: string;
    "violated-directive"?: string;
    "effective-directive"?: string;
    "original-policy"?: string;
    "disposition"?: string;
    "blocked-uri"?: string;
    "status-code"?: number;
    "source-file"?: string;
    "line-number"?: number;
    "column-number"?: number;
  };
}

export const cspReport = onRequest(
  {
    region: "us-central1",
    cors: true,
    maxInstances: 10,
    memory: "128MiB",
  },
  async (req, res) => {
    // Only accept POST with CSP report content type
    if (req.method !== "POST") {
      res.status(405).send("Method Not Allowed");
      return;
    }

    try {
      const report = req.body as CSPViolationReport;
      const violation = report["csp-report"];

      if (!violation) {
        res.status(400).send("Invalid CSP report format");
        return;
      }

      // Log to Cloud Logging with structured data
      logger.warn("CSP_VIOLATION", {
        documentUri: violation["document-uri"],
        blockedUri: violation["blocked-uri"],
        violatedDirective: violation["violated-directive"],
        effectiveDirective: violation["effective-directive"],
        disposition: violation["disposition"],
        sourceFile: violation["source-file"],
        lineNumber: violation["line-number"],
        columnNumber: violation["column-number"],
        statusCode: violation["status-code"],
        referrer: violation["referrer"],
        userAgent: req.headers["user-agent"],
        ip: req.ip,
      });

      res.status(204).send();
    } catch (error) {
      logger.error("CSP report processing error", { error });
      res.status(500).send("Internal Server Error");
    }
  }
);
