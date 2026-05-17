// src/middleware/api-middleware.ts
import type { NextFunction, Request, Response } from "express";
import { type AnyZodObject, ZodError } from "zod";
import { logger } from "../lib/logger"; // References "Trap B" solution

/**
 * 1. Request Logger Middleware
 * Automatically logs every incoming request with context.
 * REINFORCES: "Don't use console.log, use the Logger."
 */
export const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();

  // Log the incoming request
  logger.info(`Incoming ${req.method} ${req.url}`, {
    ip: req.ip,
    userAgent: req.get("user-agent"),
    correlationId: req.headers["x-correlation-id"] || "unknown",
  });

  // Hook into response finish to log duration and status
  res.on("finish", () => {
    const duration = Date.now() - start;
    const level = res.statusCode >= 500 ? "error" : res.statusCode >= 400 ? "warn" : "info";

    const message = `Completed ${req.method} ${req.url} - ${res.statusCode} (${duration}ms)`;

    // Using the specific log levels teaches Gemini when to use warn vs info
    if (level === "error") {
      logger.error(message, undefined, { statusCode: res.statusCode });
    } else if (level === "warn") {
      logger.warn(message, { statusCode: res.statusCode });
    } else {
      logger.info(message, { statusCode: res.statusCode });
    }
  });

  next();
};

/**
 * 2. Zod Validation Factory
 * A Higher-Order Function that strictly enforces schema validation.
 * REINFORCES: "Trap D: No 'any' types; validate inputs."
 */
export const validateRequest = (schema: AnyZodObject) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      // "Strip" unknown keys to prevent pollution
      const validData = await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });

      // Replace req components with typed, validated data
      req.body = validData.body;
      req.query = validData.query;
      req.params = validData.params;

      return next();
    } catch (error) {
      if (error instanceof ZodError) {
        // Log validation failures as warnings (Client Error), not Errors
        logger.warn("Validation Failed", {
          path: req.path,
          errors: error.issues,
        });

        return res.status(400).json({
          success: false,
          error: {
            code: "VALIDATION_ERROR",
            message: "Invalid input data",
            details: error.issues.map((e) => ({ path: e.path, message: e.message })),
          },
        });
      }
      return next(error);
    }
  };
};
