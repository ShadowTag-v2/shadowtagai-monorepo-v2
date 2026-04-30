"use server";

import { checkIdempotency, releaseIdempotencyLock } from "@/lib/idempotency";
import { safeAction } from "@/lib/safe-action";

/**
 * Cor.Re-Coding the Vibe — Two-Front Defense:
 *
 * Front 1 (DOM Lock): React 19 useFormStatus in SubmitButton.tsx
 *   → Disables the button while the Server Action is in-flight.
 *   → Manages user PERCEPTION ("it's working, don't touch").
 *
 * Front 2 (Edge Idempotency Lock): This file.
 *   → Redis NX lock mathematically rejects duplicate payloads.
 *   → Survives page refresh, network retry, tab duplication.
 *
 * "A UI spinner is useless if a page refresh bypasses it."
 */
export async function processOrderAction(prevState: unknown, formData: FormData) {
  const idempotencyKey = formData.get("idempotencyKey") as string;
  const orderData = formData.get("orderData") as string;

  // ──────────────────────────────────────────────────────
  // FRONT 2: The Physics Lock.
  // If the user refreshed the page while the spinner was active,
  // this instantly catches the duplicate request and halts execution.
  // ──────────────────────────────────────────────────────
  const isNew = await checkIdempotency(idempotencyKey);
  if (!isNew) {
    console.warn(`[AGNT_OS] Blocked duplicate order submission: ${idempotencyKey}`);
    return { error: "This order is already processing. Please wait." };
  }

  // ──────────────────────────────────────────────────────
  // safeAction: Wraps the entire business logic in a try/catch
  // that emails engineering on production failures instead of
  // silently swallowing errors.
  // ──────────────────────────────────────────────────────
  const result = await safeAction("processOrder", async () => {
    // TODO: Replace with real payment processing (Stripe)
    // and database insertion (Firestore/Prisma).
    await new Promise((resolve) => setTimeout(resolve, 2000));

    return { success: true as const, orderId: idempotencyKey };
  });

  if (result.error) {
    // CRITICAL: Release the idempotency lock on LEGITIMATE failure
    // so the user can retry. The lock only persists on SUCCESS
    // to prevent duplicate mutations.
    await releaseIdempotencyLock(idempotencyKey);
    return { error: result.error };
  }

  return { success: true, orderId: result.data?.orderId };
}
