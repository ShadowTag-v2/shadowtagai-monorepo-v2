/**
 * CSP Violation Report Endpoint — Cloud Function (Gen 2)
 * ══════════════════════════════════════════════════════
 *
 * Receives CSP violation reports and logs them to Cloud Logging.
 * Add report-uri or report-to directive to CSP headers pointing to this function.
 *
 * Deployed at: https://us-central1-shadowtag-omega-v4.cloudfunctions.net/cspReport
 */
Object.defineProperty(exports, '__esModule', { value: true });
exports.cspReport = void 0;
const v2_1 = require('firebase-functions/v2');
const https_1 = require('firebase-functions/v2/https');
exports.cspReport = (0, https_1.onRequest)(
  {
    region: 'us-central1',
    cors: true,
    maxInstances: 10,
    memory: '128MiB',
  },
  async (req, res) => {
    // Only accept POST with CSP report content type
    if (req.method !== 'POST') {
      res.status(405).send('Method Not Allowed');
      return;
    }
    try {
      const report = req.body;
      const violation = report['csp-report'];
      if (!violation) {
        res.status(400).send('Invalid CSP report format');
        return;
      }
      // Log to Cloud Logging with structured data
      v2_1.logger.warn('CSP_VIOLATION', {
        documentUri: violation['document-uri'],
        blockedUri: violation['blocked-uri'],
        violatedDirective: violation['violated-directive'],
        effectiveDirective: violation['effective-directive'],
        disposition: violation.disposition,
        sourceFile: violation['source-file'],
        lineNumber: violation['line-number'],
        columnNumber: violation['column-number'],
        statusCode: violation['status-code'],
        referrer: violation.referrer,
        userAgent: req.headers['user-agent'],
        ip: req.ip,
      });
      res.status(204).send();
    } catch (error) {
      v2_1.logger.error('CSP report processing error', { error });
      res.status(500).send('Internal Server Error');
    }
  },
);
//# sourceMappingURL=cspReport.js.map
