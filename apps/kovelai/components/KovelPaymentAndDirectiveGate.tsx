/**
 * @fileoverview Kovel Payment & Directive Gate
 *
 * The clickwrap that executes the Stripe transaction and legally transforms
 * the AI into a privileged agent under United States v. Heppner (S.D.N.Y. 2026).
 *
 * This component:
 * 1. Renders the Kovel privilege attestation
 * 2. Collects Stripe payment via PaymentElement
 * 3. On payment success, mints an S.E.U. token
 * 4. Unlocks the Edge Router connection
 *
 * The payment IS the security perimeter.
 */

'use client';

import { useState, type FormEvent } from 'react';
import {
  PaymentElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';

interface KovelPaymentGateProps {
  lawyerName: string;
  feeAmount: number;
  onPaymentSuccess: (seuToken: string) => void;
}

export default function KovelPaymentGate({
  lawyerName,
  feeAmount,
  onPaymentSuccess,
}: KovelPaymentGateProps) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAuthorizeAndPay = async (e: FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setIsProcessing(true);
    setError(null);

    // 1. Process upfront payment directly to Lawyer's Stripe Connect Account
    const { error: stripeError, paymentIntent } =
      await stripe.confirmPayment({
        elements,
        redirect: 'if_required',
      });

    if (stripeError) {
      setError(stripeError.message ?? 'Payment failed.');
      setIsProcessing(false);
      return;
    }

    if (paymentIntent?.status === 'succeeded') {
      // 2. Payment clears → mint S.E.U. token for the session
      const res = await fetch('/api/auth/mint-seu-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chargeId: paymentIntent.id }),
      });

      if (!res.ok) {
        setError('Token minting failed. Contact your attorney.');
        setIsProcessing(false);
        return;
      }

      const { seuToken } = await res.json();
      onPaymentSuccess(seuToken); // Unlocks the Edge Router connection
    }

    setIsProcessing(false);
  };

  return (
    <div className="kovel-gate fixed inset-0 bg-black/95 text-white p-8 flex flex-col justify-center z-50 max-w-md mx-auto">
      <h2 className="text-3xl font-light tracking-widest mb-4 text-emerald-400">
        KOVELAI : PRIVILEGED ENCLAVE
      </h2>

      <div className="bg-gray-900 p-6 border border-gray-800 rounded mb-6 text-sm font-mono text-gray-400 leading-relaxed">
        Pursuant to <em>United States v. Heppner</em> (S.D.N.Y. 2026), you
        acknowledge: <br />
        <br />
        1. You are accessing a Closed Enterprise AI System at the{' '}
        <strong>express direction of {lawyerName}</strong>.<br />
        2. Your search activity (Medical, Financial, Web) and uploads are
        protected Attorney Work-Product.
        <br />
        3.{' '}
        <strong>
          FEE: You agree to a ${feeAmount} upfront retainer per triage session
        </strong>
        , billed directly to your attorney&apos;s operating account.
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700 text-red-300 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleAuthorizeAndPay}>
        <div className="bg-white p-4 rounded mb-4">
          <PaymentElement />
        </div>
        <button
          type="submit"
          disabled={isProcessing || !stripe}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 text-white font-bold py-4 rounded transition-all tracking-wide"
        >
          {isProcessing
            ? 'SECURING TUNNEL...'
            : `AUTHORIZE & PAY $${feeAmount}`}
        </button>
      </form>
    </div>
  );
}
