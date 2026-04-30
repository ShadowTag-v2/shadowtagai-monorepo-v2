"use server";

import { checkIdempotency } from "@/lib/idempotency";
// Assuming you have the safe-action wrapper from our previous AGNT_OS implementation
// import { safeAction } from "@/lib/safe-action"; 

export async function processOrderAction(prevState: any, formData: FormData) {
  const idempotencyKey = formData.get("idempotencyKey") as string;
  const orderData = formData.get("orderData") as string;

  //  2026 Guardrail: The Physics Lock.
  // If the user refreshed the page while the spinner was active, 
  // this instantly catches the duplicate request and halts execution.
  const isNew = await checkIdempotency(idempotencyKey);
  if (!isNew) {
    console.warn(`[AGNT_OS] Blocked duplicate order submission: ${idempotencyKey}`);
    return { error: "This order is already processing. Please wait." };
  }

  try {
    // Simulate 2-second payment processing delay
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    // Process real Database insertion here...

    return { success: true };
  } catch (error) {
    // CRITICAL: If the database transaction fails legitimately, you must release the lock
    // so the user can attempt to checkout again.
    // await redis.del(`idempotency:${idempotencyKey}`);
    return { error: "Payment failed. Engineering has been notified." };
  }
}
