"use client";

import { useActionState } from "react";
import { SubmitButton } from "@/components/SubmitButton";
import { processOrderAction } from "./actions";

export function CheckoutForm({ idempotencyKey }: { idempotencyKey: string }) {
  // React 19: Binds the Server Action to the form UI safely.
  const [state, formAction] = useActionState(processOrderAction, null);

  return (
    <form action={formAction} className="flex flex-col gap-4 border p-6 rounded-lg shadow-sm">
      <input type="hidden" name="idempotencyKey" value={idempotencyKey} />
      
      <div>
        <label htmlFor="orderData" className="block text-sm font-medium">Order Details</label>
        <input 
          id="orderData" 
          name="orderData" 
          type="text" 
          required 
          className="mt-1 block w-full rounded-md border p-2"
        />
      </div>

      {state?.error && (
        <div className="p-3 text-sm text-red-700 bg-red-50 rounded-md border border-red-200">
          {state.error}
        </div>
      )}
      
      {state?.success && (
        <div className="p-3 text-sm text-green-700 bg-green-50 rounded-md border border-green-200">
          Order secured!
        </div>
      )}

      {/* The DOM Lock engages automatically. */}
      <SubmitButton pendingText="Securing Order...">
        Submit Order
      </SubmitButton>
    </form>
  );
}
