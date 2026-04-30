"use client";
import { useFormStatus } from "react-dom";
export function SubmitButton({ children }: { children: React.ReactNode }) {
  const { pending } = useFormStatus();
  return <button type="submit" disabled={pending} style={{ opacity: pending ? 0.5 : 1 }}>{pending ? "Loading... (Cor.UX Guard)" : children}</button>;
}
