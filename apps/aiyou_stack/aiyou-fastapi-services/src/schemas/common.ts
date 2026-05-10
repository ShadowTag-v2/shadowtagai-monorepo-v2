// src/schemas/common.ts
import { z } from 'zod';

/**
 * Base schema for generic API responses.
 * Enforces standardized response structure.
 */
export const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    error: z
      .object({
        code: z.string(),
        message: z.string(),
      })
      .optional(),
    timestamp: z.string().datetime(),
  });

/**
 * Example User Schema
 * Reinforces: No "any", strict typing, and validation logic.
 */
export const UserProfileSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email('Invalid email format'),
  username: z.string().min(3, 'Username must be at least 3 chars').max(20),
  role: z.enum(['admin', 'editor', 'viewer']),
  preferences: z.object({
    theme: z.enum(['light', 'dark', 'system']).default('system'),
    notifications: z.boolean().default(true),
  }),
  // "Trap A" reinforcement: Ensure dates are handled as strings (ISO) or Date objects, not moment moments
  lastLogin: z.string().datetime().nullable(),
});

// Type Inference - The "Reward" for using Zod
// Developers don't need to manually write interfaces; they export this type.
export type UserProfile = z.infer<typeof UserProfileSchema>;

/**
 * Validator Helper
 * Usage: const validData = validateInput(UserProfileSchema, rawData);
 */
export function validateInput<T>(schema: z.ZodSchema<T>, input: unknown): T {
  const result = schema.safeParse(input);
  if (!result.success) {
    // This throws a structured error that middleware can catch
    throw new Error(`Validation Failed: ${result.error.issues.map((i) => i.message).join(', ')}`);
  }
  return result.data;
}
