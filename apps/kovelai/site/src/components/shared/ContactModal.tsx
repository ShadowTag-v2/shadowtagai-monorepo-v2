// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

'use client';

import { type FormEvent, useCallback, useEffect, useRef, useState } from 'react';

interface ContactModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ContactModal({ isOpen, onClose }: ContactModalProps) {
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  // Focus trap + Escape handler
  useEffect(() => {
    if (!isOpen) return;

    // Focus the close button when modal opens
    setTimeout(() => closeButtonRef.current?.focus(), 50);

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
        return;
      }

      // Focus trap: Tab cycling within modal
      if (e.key === 'Tab' && modalRef.current) {
        const focusable = modalRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input:not([type="hidden"]), select, textarea, [tabindex]:not([tabindex="-1"])',
        );
        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };

    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = '';
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  const handleClose = useCallback(() => {
    if (submitted) setSubmitted(false);
    onClose();
  }, [submitted, onClose]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitting(true);
    const form = e.currentTarget;
    const data = new FormData(form);

    try {
      await fetch('https://capturelead-767252945109.us-central1.run.app', {
        method: 'POST',
        body: data,
      });
      setSubmitted(true);
      form.reset();
      // Show toast
      const toast = document.getElementById('toast');
      if (toast) {
        toast.classList.add('toast--visible');
        setTimeout(() => toast.classList.remove('toast--visible'), 4000);
      }
      setTimeout(handleClose, 2000);
    } catch {
      // Silent fail with toast
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Toast */}
      <div id="toast" className="toast" role="status" aria-live="polite">
        ✓ Inquiry received. Our team will respond within 24 hours.
      </div>

      {/* Modal */}
      <div
        className="modal-overlay modal-overlay--visible"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modalTitle"
        onClick={(e) => {
          if (e.target === e.currentTarget) handleClose();
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') handleClose();
        }}
      >
        <div className="modal-content" ref={modalRef}>
          <div className="flex justify-between items-center mb-8">
            <h3 id="modalTitle" className="text-2xl font-bold">
              Contact KovelAI
            </h3>
            <button
              type="button"
              ref={closeButtonRef}
              onClick={handleClose}
              className="bg-transparent border-none text-[#998f81] cursor-pointer text-2xl hover:text-primary-text transition-colors"
              aria-label="Close modal"
            >
              ×
            </button>
          </div>

          {submitted ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-4">✓</div>
              <p className="text-primary-text font-medium">Inquiry received!</p>
              <p className="text-sm text-secondary-text mt-2">
                Our team will respond within 24 hours.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {/* Honeypot */}
              <input
                type="text"
                name="_honey"
                className="hidden"
                tabIndex={-1}
                autoComplete="off"
              />
              <input type="hidden" name="sheet_name" value="KovelAI" />
              <input type="hidden" name="source" value="kovelai.com" />

              <div className="grid gap-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label
                      htmlFor="kv-name"
                      className="block text-[0.65rem] uppercase tracking-[0.15em] text-[#998f81] mb-2"
                    >
                      Full Name
                    </label>
                    <input
                      id="kv-name"
                      name="name"
                      type="text"
                      required
                      className="modal-input"
                      placeholder="Jane Smith"
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="kv-firm"
                      className="block text-[0.65rem] uppercase tracking-[0.15em] text-[#998f81] mb-2"
                    >
                      Firm / Organization
                    </label>
                    <input
                      id="kv-firm"
                      name="company"
                      type="text"
                      className="modal-input"
                      placeholder="Smith & Associates"
                    />
                  </div>
                </div>
                <div>
                  <label
                    htmlFor="kv-email"
                    className="block text-[0.65rem] uppercase tracking-[0.15em] text-[#998f81] mb-2"
                  >
                    Email
                  </label>
                  <input
                    id="kv-email"
                    name="email"
                    type="email"
                    required
                    className="modal-input"
                    placeholder="you@company.com"
                  />
                </div>
                <div>
                  <label
                    htmlFor="kv-subject"
                    className="block text-[0.65rem] uppercase tracking-[0.15em] text-[#998f81] mb-2"
                  >
                    Subject
                  </label>
                  <select
                    id="kv-subject"
                    name="inquiry_type"
                    className="modal-input"
                    style={{ appearance: 'auto' }}
                  >
                    <option value="demo">Schedule a Demo</option>
                    <option value="enterprise">Enterprise Pricing</option>
                    <option value="compliance">Compliance Question</option>
                    <option value="general">General Inquiry</option>
                  </select>
                </div>
                <div>
                  <label
                    htmlFor="kv-message"
                    className="block text-[0.65rem] uppercase tracking-[0.15em] text-[#998f81] mb-2"
                  >
                    Message
                  </label>
                  <textarea
                    id="kv-message"
                    name="message"
                    rows={4}
                    className="modal-input"
                    placeholder="Tell us about your firm's needs..."
                    style={{ resize: 'vertical' }}
                  />
                </div>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-gold w-full justify-center text-sm disabled:opacity-50"
                >
                  {submitting ? 'Submitting…' : 'Submit Inquiry'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </>
  );
}
