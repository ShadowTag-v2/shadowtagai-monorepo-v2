"use client";

import { useFormStatus } from "react-dom";
import { Loader2 } from "lucide-react";

interface SubmitButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  pendingText?: string;
}

export function SubmitButton({ children, pendingText = "Processing...", ...props }: SubmitButtonProps) {
  // AGNT_OS Cognitive Guardrail: React 19 natively tracks the Server Action in-flight status.
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      // Physical lock: The user mathematically cannot double-click the button.
      disabled={pending || props.disabled}
      aria-disabled={pending}
      className={`relative inline-flex items-center justify-center rounded-md bg-black px-4 py-2 text-sm font-medium text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${props.className || ""}`}
      {...props}
    >
      {pending ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin text-white/80" aria-hidden="true" />
          {pendingText}
        </>
      ) : (
        children
      )}
    </button>
  );
}
