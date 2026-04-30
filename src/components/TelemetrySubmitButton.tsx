"use client";

/**
 * TelemetrySubmitButton — Panopticon-Wired Form Submit
 *
 * Cor.Re-Coding the Vibe: This extends SubmitButton with automatic
 * telemetry tracking for form submission lifecycle:
 *
 *   1. Button rendered → checkout.started
 *   2. Button clicked → checkout.submitted
 *   3. Form completes → checkout.success / checkout.error
 *   4. Duplicate blocked → checkout.duplicate_blocked
 *
 * The two-front defense remains intact:
 *   Front 1 (DOM Lock): useFormStatus disables the button
 *   Front 2 (Edge Lock): Redis NX in checkout/actions.ts
 *   Front 3 (Observability): This component tracks the full lifecycle
 */

import { useFormStatus } from "react-dom";
import { useEffect, useRef } from "react";
import { Loader2 } from "lucide-react";
import { usePanopticon } from "@/hooks/usePanopticon";

interface TelemetrySubmitButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  pendingText?: string;
  /** Optional: form name for telemetry grouping */
  formName?: string;
}

export function TelemetrySubmitButton({
  children,
  pendingText = "Processing...",
  formName = "checkout",
  ...props
}: TelemetrySubmitButtonProps) {
  const { pending } = useFormStatus();
  const { trackCheckout, track } = usePanopticon();
  const wasSubmitting = useRef(false);
  const hasTrackedStart = useRef(false);

  // Track form mount (checkout started)
  useEffect(() => {
    if (hasTrackedStart.current) return;
    hasTrackedStart.current = true;
    trackCheckout("started");
  }, [trackCheckout]);

  // Track submission lifecycle transitions
  useEffect(() => {
    if (pending && !wasSubmitting.current) {
      // Transition: idle → pending (user clicked submit)
      wasSubmitting.current = true;
      trackCheckout("submitted");
      track("form.submit_initiated", {
        form_name_hash: hashString(formName),
      });
    } else if (!pending && wasSubmitting.current) {
      // Transition: pending → idle (action completed)
      wasSubmitting.current = false;
      // Note: success/error is tracked by the server action itself,
      // but we track the UI transition for timing correlation
      track("form.submit_completed", {
        form_name_hash: hashString(formName),
      });
    }
  }, [pending, trackCheckout, track, formName]);

  return (
    <button
      type="submit"
      disabled={pending || props.disabled}
      aria-disabled={pending}
      aria-busy={pending}
      className={`relative inline-flex items-center justify-center rounded-md bg-black px-4 py-2 text-sm font-medium text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-black ${props.className || ""}`}
      {...props}
    >
      {pending ? (
        <>
          <Loader2
            className="mr-2 h-4 w-4 animate-spin text-white/80"
            aria-hidden="true"
          />
          <span aria-live="polite">{pendingText}</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────
// Utility: Hash to prevent PII leakage in metadata
// ─────────────────────────────────────────────────────────────

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const chr = str.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0;
  }
  return Math.abs(hash);
}
