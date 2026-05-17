import { Redis } from "@upstash/redis";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

export async function checkIdempotency(transactionId: string): Promise<boolean> {
  if (!transactionId) return false;

  // NX (Not eXists): Only set if the key does not exist.
  // EX (Expire): Keeps the Redis cache clean by purging the lock after 24 hours.
  // Upstash returns "OK" if the set was successful, or null if the key already existed.
  const lock = await redis.set(`idempotency:${transactionId}`, "LOCKED", { nx: true, ex: 86400 });

  return lock === "OK";
}

/**
 * Release an idempotency lock after a LEGITIMATE transaction failure.
 * This allows the user to retry the same operation.
 *
 * CRITICAL: Only call this when the business logic fails (e.g., payment
 * declined, database write error). NEVER call this on success — the lock
 * must persist to prevent duplicate mutations.
 */
export async function releaseIdempotencyLock(transactionId: string): Promise<void> {
  if (!transactionId) return;
  await redis.del(`idempotency:${transactionId}`);
}
