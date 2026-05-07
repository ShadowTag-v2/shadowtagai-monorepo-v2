'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

interface SecuritySettingsProps {
  userId: string;
  stripeCustomerId?: string;
}

export default function SecuritySettings({ userId, stripeCustomerId }: SecuritySettingsProps) {
  const [showNukeModal, setShowNukeModal] = useState(false);
  const [confirmationText, setConfirmationText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [captchaVerified, setCaptchaVerified] = useState(false);
  const [captchaChallenge, setCaptchaChallenge] = useState('');

  const router = useRouter();

  // Simple behavioral CAPTCHA (in production, replace with proper implementation)
  const generateCaptcha = () => {
    const challenges = [
      "Type the word 'SECURE' backwards",
      'What is 7 + 3?',
      "Type 'SHADOWTAG' in all caps",
    ];
    const randomIndex = Math.floor(Math.random() * challenges.length);
    setCaptchaChallenge(challenges[randomIndex]);
    setCaptchaVerified(false);
  };

  const verifyCaptcha = (input: string) => {
    const expected = captchaChallenge.toLowerCase().replace(/[^a-z0-9]/g, '');
    const userInput = input.toLowerCase().replace(/[^a-z0-9]/g, '');

    if (expected === userInput || input === 'SECURE' || input === '10' || input === 'SHADOWTAG') {
      setCaptchaVerified(true);
      return true;
    }
    return false;
  };

  const handleNukeAccount = async () => {
    if (confirmationText !== 'NUKE MY DATA') {
      setError('Please type "NUKE MY DATA" exactly to confirm.');
      return;
    }

    if (!captchaVerified) {
      setError('Please complete the security verification.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/security/nuke-account', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          stripeCustomerId,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to delete account');
      }

      setSuccess(true);

      // Clear session and redirect
      setTimeout(() => {
        router.push('/goodbye');
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred. Please try again.');
      setIsLoading(false);
    }
  };

  const openNukeModal = () => {
    setShowNukeModal(true);
    setConfirmationText('');
    setError('');
    setSuccess(false);
    setCaptchaVerified(false);
    generateCaptcha();
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-zinc-900 border border-red-500/30 rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center">
            <span className="text-red-500 text-xl">⚠️</span>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Danger Zone</h2>
            <p className="text-sm text-zinc-400">Irreversible actions</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-zinc-800/50 rounded-xl border border-zinc-700">
            <h3 className="font-medium text-white mb-2">Delete My Account</h3>
            <p className="text-sm text-zinc-400 mb-4">
              Permanently delete your account and all associated data. This action cannot be undone.
            </p>

            <button
              onClick={openNukeModal}
              className="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Nuke My Data
            </button>
          </div>
        </div>
      </div>

      {/* Nuke Modal */}
      {showNukeModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-zinc-900 border border-red-500/50 rounded-2xl max-w-md w-full p-8">
            {!success ? (
              <>
                <div className="text-center mb-6">
                  <div className="w-16 h-16 mx-auto rounded-full bg-red-500/10 flex items-center justify-center mb-4">
                    <span className="text-4xl">💥</span>
                  </div>
                  <h3 className="text-2xl font-semibold text-white mb-2">Delete Everything?</h3>
                  <p className="text-zinc-400 text-sm">
                    This will permanently delete your account, all data, billing information, and
                    revoke all sessions.
                  </p>
                </div>

                {/* CAPTCHA */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-zinc-400 mb-2">
                    Security Verification
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={captchaChallenge}
                      readOnly
                      className="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-zinc-400 text-sm"
                    />
                    <button
                      onClick={generateCaptcha}
                      className="px-3 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 rounded-lg text-sm"
                    >
                      ↻
                    </button>
                  </div>
                  <input
                    type="text"
                    placeholder="Type the answer here"
                    className="w-full mt-2 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white"
                    onChange={(e) => verifyCaptcha(e.target.value)}
                  />
                  {captchaVerified && <p className="text-emerald-400 text-xs mt-1">✓ Verified</p>}
                </div>

                {/* Confirmation Input */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-zinc-400 mb-2">
                    Type <span className="font-mono text-red-400">NUKE MY DATA</span> to confirm
                  </label>
                  <input
                    type="text"
                    value={confirmationText}
                    onChange={(e) => setConfirmationText(e.target.value)}
                    placeholder="NUKE MY DATA"
                    className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white font-mono text-sm"
                    disabled={isLoading}
                    onPaste={(e) => e.preventDefault()}
                  />
                </div>

                {error && (
                  <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                    {error}
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowNukeModal(false)}
                    className="flex-1 px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-medium transition-colors"
                    disabled={isLoading}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleNukeAccount}
                    disabled={isLoading || confirmationText !== 'NUKE MY DATA' || !captchaVerified}
                    className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-red-900 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Shredding...
                      </>
                    ) : (
                      'Permanently Delete'
                    )}
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <div className="w-20 h-20 mx-auto rounded-full bg-emerald-500/10 flex items-center justify-center mb-6">
                  <span className="text-5xl">✅</span>
                </div>
                <h3 className="text-2xl font-semibold text-white mb-3">Account Deleted</h3>
                <p className="text-zinc-400 mb-6">
                  All your data has been cryptographically shredded. You will be redirected shortly.
                </p>
                <div className="text-xs text-zinc-500">Thank you for using ShadowTag AI</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
