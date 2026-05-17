/**
 * Structured logging with GCP Cloud Logging integration
 */

import { LoggingWinston } from "@google-cloud/logging-winston";
import winston from "winston";

const loggingWinston = new LoggingWinston({
  projectId: process.env.ANTHROPIC_VERTEX_PROJECT_ID,
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS, // Only for local dev
});

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json(),
  ),
  defaultMeta: {
    service: "shadowtagai-orchestrator",
    environment: process.env.NODE_ENV || "development",
  },
  transports: [
    // Console for local development
    new winston.transports.Console({
      format: winston.format.combine(winston.format.colorize(), winston.format.simple()),
    }),
    // GCP Cloud Logging for production
    ...(process.env.NODE_ENV === "production" ? [loggingWinston] : []),
  ],
});

// Create child logger with context
export function createLogger(context: Record<string, any>) {
  return logger.child(context);
}
