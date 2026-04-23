/**
 * Structured Cloud Logging — KovelAI
 *
 * Replaces console.* with structured JSON logs compatible with
 * Google Cloud Logging severity levels and trace context.
 *
 * Usage:
 *   import { logger } from '@/lib/observability/structured-logger';
 *   logger.info('Operation completed', { firmId, sessionId, durationMs: 42 });
 *
 * In Cloud Run, these JSON logs are automatically parsed by Cloud Logging.
 * Locally, they pretty-print with color-coded severity.
 */

type Severity = 'DEBUG' | 'INFO' | 'NOTICE' | 'WARNING' | 'ERROR' | 'CRITICAL' | 'ALERT';

interface LogEntry {
  severity: Severity;
  message: string;
  timestamp: string;
  'logging.googleapis.com/trace'?: string;
  'logging.googleapis.com/spanId'?: string;
  'logging.googleapis.com/labels'?: Record<string, string>;
  component?: string;
  [key: string]: unknown;
}

const IS_CLOUD_RUN = !!process.env.K_SERVICE;
const PROJECT_ID = process.env.GCLOUD_PROJECT || 'shadowtag-omega-v4';

/**
 * PII fields that must NEVER appear in logs (Cor.30 R11).
 */
const PII_FIELDS = new Set([
  'email',
  'password',
  'ssn',
  'creditCard',
  'cardNumber',
  'token',
  'secret',
  'apiKey',
  'authorization',
  'cookie',
  'phoneNumber',
  'address',
  'dateOfBirth',
  'ipAddress',
]);

/**
 * Redact PII from log payloads.
 */
function redactPII(data: Record<string, unknown>): Record<string, unknown> {
  const redacted: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(data)) {
    if (PII_FIELDS.has(key) || PII_FIELDS.has(key.toLowerCase())) {
      redacted[key] = '[REDACTED]';
    } else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      redacted[key] = redactPII(value as Record<string, unknown>);
    } else {
      redacted[key] = value;
    }
  }

  return redacted;
}

/**
 * Format a structured log entry.
 */
function formatEntry(
  severity: Severity,
  message: string,
  data?: Record<string, unknown>,
  component?: string,
  traceId?: string,
): LogEntry {
  const entry: LogEntry = {
    severity,
    message,
    timestamp: new Date().toISOString(),
  };

  if (component) entry.component = component;

  if (traceId && IS_CLOUD_RUN) {
    entry['logging.googleapis.com/trace'] = `projects/${PROJECT_ID}/traces/${traceId}`;
  }

  if (data) {
    const safe = redactPII(data);
    Object.assign(entry, safe);
  }

  return entry;
}

/**
 * Emit a log entry — JSON to stdout in Cloud Run, pretty-print locally.
 */
function emit(entry: LogEntry): void {
  if (IS_CLOUD_RUN) {
    // Cloud Logging auto-parses JSON from stdout
    process.stdout.write(`${JSON.stringify(entry)}\n`);
  } else {
    const colors: Record<Severity, string> = {
      DEBUG: '\x1b[90m',
      INFO: '\x1b[36m',
      NOTICE: '\x1b[34m',
      WARNING: '\x1b[33m',
      ERROR: '\x1b[31m',
      CRITICAL: '\x1b[35m',
      ALERT: '\x1b[41m\x1b[37m',
    };
    const reset = '\x1b[0m';
    const color = colors[entry.severity] || '';
    const { severity, message, timestamp, ...rest } = entry;
    const extra = Object.keys(rest).length > 0 ? ` ${JSON.stringify(rest)}` : '';
    // eslint-disable-next-line no-console
    console.log(`${color}[${severity}]${reset} ${timestamp} ${message}${extra}`);
  }
}

/**
 * Create a scoped logger for a specific component.
 */
export function createLogger(component: string, defaultTraceId?: string) {
  return {
    debug: (msg: string, data?: Record<string, unknown>) =>
      emit(formatEntry('DEBUG', msg, data, component, defaultTraceId)),
    info: (msg: string, data?: Record<string, unknown>) =>
      emit(formatEntry('INFO', msg, data, component, defaultTraceId)),
    notice: (msg: string, data?: Record<string, unknown>) =>
      emit(formatEntry('NOTICE', msg, data, component, defaultTraceId)),
    warn: (msg: string, data?: Record<string, unknown>) =>
      emit(formatEntry('WARNING', msg, data, component, defaultTraceId)),
    error: (msg: string, data?: Record<string, unknown>) =>
      emit(formatEntry('ERROR', msg, data, component, defaultTraceId)),
    critical: (msg: string, data?: Record<string, unknown>) =>
      emit(formatEntry('CRITICAL', msg, data, component, defaultTraceId)),
    alert: (msg: string, data?: Record<string, unknown>) =>
      emit(formatEntry('ALERT', msg, data, component, defaultTraceId)),
  };
}

/** Default logger instance */
export const logger = createLogger('kovelai');
