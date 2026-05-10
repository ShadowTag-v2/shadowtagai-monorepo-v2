'use client';

import type React from 'react';
import { useState } from 'react';

type Step = 'INITIAL' | 'RESEARCHING_BAD' | 'RESEARCHING_GOOD' | 'JUDGE6_INTERVENTION' | 'LOCKED';

export default function CorpInvisibleDemo() {
  const [step, setStep] = useState<Step>('INITIAL');
  const [inputValue, setInputValue] = useState('');
  const [violationCount, setViolationCount] = useState(0);

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputValue.trim()) return;

    const newViolationCount = violationCount + 1;
    setViolationCount(newViolationCount);

    if (newViolationCount >= 3) {
      setStep('LOCKED');
      return;
    }

    setStep('RESEARCHING_BAD');

    // Simulate invisible interception
    setTimeout(() => {
      setStep('JUDGE6_INTERVENTION');
    }, 1500); // Intercepts before the page even navigates
  };

  const executeMitigation = (prompt: string) => {
    setInputValue(prompt);
    setStep('RESEARCHING_GOOD');

    setTimeout(() => {
      // Return to initial state, simulating a safe search completion
      setStep('INITIAL');
      setInputValue('');
    }, 2000);
  };

  if (step === 'LOCKED') {
    return (
      <div className="min-h-screen bg-red-950 flex flex-col items-center justify-center p-8 font-mono">
        <div className="max-w-xl w-full bg-black border border-red-600 rounded-lg p-8 shadow-[0_0_50px_rgba(220,38,38,0.3)] text-center">
          <svg
            className="w-24 h-24 text-red-600 mx-auto mb-6 animate-pulse"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            ></path>
          </svg>
          <h1 className="text-3xl font-bold text-red-500 mb-2 uppercase tracking-widest">
            Workstation Locked
          </h1>
          <h2 className="text-lg text-white font-bold mb-6">Judge 6 Level 5 Violation Triggered</h2>
          <p className="text-gray-300 text-sm mb-6 leading-relaxed">
            Egregious override attempted following recurrent mitigation warnings. This constitutes a
            Level 5 violation under standard corporate data doctrine. Network access has been
            severed at the Edge.
          </p>
          <div className="bg-red-950/50 border border-red-800 p-4 rounded text-left mb-6 font-mono text-xs text-red-200">
            [SYSTEM LOG: Executing hard kill on web process]
            <br />
            [SYSTEM LOG: DNS routed to blackhole]
            <br />
            [SYSTEM LOG: Alerting Site Reliability & Legal Compliance...]
          </div>
          <div className="text-red-400 font-bold uppercase tracking-widest animate-pulse">
            Calling Management...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col relative font-sans text-sm">
      {/* Top Right Nav Mock */}
      <div className="flex justify-end p-4 space-x-4 items-center text-gray-700">
        <span className="hover:underline cursor-not-allowed text-gray-400">Gmail</span>
        <span className="hover:underline cursor-not-allowed text-gray-400">Images</span>
        <svg
          className="w-6 h-6 fill-current cursor-pointer text-gray-600 hover:bg-gray-100 p-1 rounded-full bg-transparent transition-colors"
          viewBox="0 0 24 24"
        >
          <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
        </svg>
        <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold">
          P
        </div>
      </div>

      {/* Main Search Area */}
      <div className="flex-1 flex flex-col items-center justify-center -mt-24">
        {/* Google Logo Mock */}
        <div className="text-[5.5rem] font-bold tracking-tighter mb-6 select-none flex">
          <span className="text-[#4285F4]">G</span>
          <span className="text-[#EA4335]">o</span>
          <span className="text-[#FBBC05]">o</span>
          <span className="text-[#4285F4]">g</span>
          <span className="text-[#34A853]">l</span>
          <span className="text-[#EA4335]">e</span>
        </div>

        <form onSubmit={handleSearchSubmit} className="w-full max-w-[584px] px-4">
          <div className="relative flex items-center w-full h-12 rounded-full border border-gray-200 hover:shadow-md focus-within:shadow-md bg-white transition-shadow px-4">
            <svg
              className="w-4 h-4 text-gray-400 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              ></path>
            </svg>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="flex-1 outline-none text-base text-black"
              disabled={
                step === 'RESEARCHING_BAD' ||
                step === 'RESEARCHING_GOOD' ||
                step === 'JUDGE6_INTERVENTION'
              }
            />
            {step === 'RESEARCHING_BAD' && (
              <div className="absolute right-4 w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            )}
            {step === 'RESEARCHING_GOOD' && (
              <div className="absolute right-4 w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
            )}
            <div className="flex items-center space-x-3 ml-3">
              <svg
                className="w-5 h-5 cursor-pointer text-[#4285f4]"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path fill="none" d="M0 0h24v24H0z" />
                <path
                  d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"
                  fill="currentColor"
                />
              </svg>
              <svg className="w-5 h-5 cursor-pointer" viewBox="0 0 24 24">
                <path
                  d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"
                  fill="#fbbc05"
                />
              </svg>
            </div>
          </div>

          <div className="flex justify-center mt-7 space-x-3">
            <button
              type="button"
              type="button"
              onClick={handleSearchSubmit}
              className="bg-[#f8f9fa] border border-[#f8f9fa] hover:border-[#dadce0] hover:shadow-sm text-[#3c4043] rounded px-4 py-2 hover:bg-white focus:outline-none transition-all"
            >
              Google Search
            </button>
            <button
              type="button"
              type="button"
              className="bg-[#f8f9fa] border border-[#f8f9fa] hover:border-[#dadce0] hover:shadow-sm text-[#3c4043] rounded px-4 py-2 hover:bg-white focus:outline-none transition-all"
            >
              I&apos;m Feeling Lucky
            </button>
          </div>
        </form>

        <div className="text-xs text-[#70757a] mt-8">
          Google offered in: <span className="text-gray-400 cursor-not-allowed mx-1">Français</span>{' '}
          <span className="text-gray-400 cursor-not-allowed mx-1">Español</span>
        </div>
      </div>

      {/* Footer Mock */}
      <div className="bg-[#f2f2f2] text-[#70757a] flex flex-col">
        <div className="px-8 py-3 border-b border-[#dadce0]">United States</div>
        <div className="flex justify-between px-8 py-3">
          <div className="flex space-x-6">
            <span className="hover:underline cursor-not-allowed text-gray-400">About</span>
            <span className="hover:underline cursor-not-allowed text-gray-400">Advertising</span>
            <span className="hover:underline cursor-not-allowed text-gray-400">Business</span>
            <span className="hover:underline cursor-not-allowed text-gray-400">
              How Search works
            </span>
          </div>
          <div className="flex space-x-6">
            <span className="hover:underline cursor-not-allowed text-gray-400">Privacy</span>
            <span className="hover:underline cursor-not-allowed text-gray-400">Terms</span>
            <span className="hover:underline cursor-not-allowed text-gray-400">Settings</span>
          </div>
        </div>
      </div>

      {/* INVISIBLE JUDGE 6 INTERVENTION OVERLAY */}
      {step === 'JUDGE6_INTERVENTION' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#111] border border-red-500/50 rounded-xl shadow-[0_20px_60px_rgba(0,0,0,0.8)] max-w-2xl w-full p-0 overflow-hidden text-white font-mono">
            {/* Header */}
            <div className="bg-red-900/30 border-b border-red-500/30 p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full flex items-center justify-center bg-red-500/20 text-red-500 ring-2 ring-red-500/50">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    ></path>
                  </svg>
                </div>
                <div>
                  <h3 className="text-red-400 font-bold uppercase tracking-wider text-sm">
                    Corporate Network Shield
                  </h3>
                  <div className="text-[10px] text-gray-400 uppercase tracking-widest">
                    Judge 6 Intervention Triggered
                  </div>
                </div>
              </div>
              <div className="text-xs text-red-400 font-bold uppercase tracking-[0.2em] animate-pulse">
                Request Intercepted
              </div>
            </div>

            {/* Body */}
            <div className="p-6">
              <p className="text-gray-200 text-sm leading-relaxed mb-6">
                Your web request{' '}
                <span className="text-emerald-400 bg-emerald-900/30 px-2 py-0.5 rounded ml-1">
                  "{inputValue}"
                </span>{' '}
                has been halted. This parameter violates our internal data governance policies or
                accesses unauthorized domains.
              </p>

              <details className="bg-black/60 border border-gray-800 rounded p-3 mb-6 cursor-pointer outline-none">
                <summary className="text-gray-400 text-xs font-bold uppercase tracking-wider outline-none select-none flex items-center justify-between">
                  Expand: Violation Reason
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M19 9l-7 7-7-7"
                    ></path>
                  </svg>
                </summary>
                <div className="text-gray-400 text-xs mt-3 leading-relaxed border-t border-gray-800 pt-3">
                  <strong>Violation Code 403.9:</strong> You attempted to initiate an unauthorized
                  search query or recursive traversal targeting explicitly blacklisted assets or
                  high-risk legal queries. Applying standard mitigation protocols.
                </div>
              </details>

              <div className="text-xs text-gray-400 mb-3 font-semibold tracking-widest uppercase">
                Select an approved compliant action:
              </div>
              <div className="space-y-3">
                <button
                  type="button"
                  onClick={() =>
                    executeMitigation('Analyze public SEC filings and anonymized market data')
                  }
                  className="w-full text-left bg-[#1B103C]/40 hover:bg-[#2a1b5c] border border-indigo-500/30 hover:border-indigo-400 px-4 py-3 rounded text-indigo-300 hover:text-white transition-all shadow-sm"
                >
                  1. Refine query to: Public SEC filings & Market Data
                </button>
                <button
                  type="button"
                  onClick={() =>
                    executeMitigation('Synthesize verified academic papers on the topic')
                  }
                  className="w-full text-left bg-[#1B103C]/40 hover:bg-[#2a1b5c] border border-indigo-500/30 hover:border-indigo-400 px-4 py-3 rounded text-indigo-300 hover:text-white transition-all shadow-sm"
                >
                  2. Refine query to: Verified Academic Papers
                </button>
                <button
                  type="button"
                  onClick={() =>
                    executeMitigation('Request official API access via Data Compliance Officer')
                  }
                  className="flex items-center justify-between w-full text-left bg-emerald-900/20 hover:bg-emerald-800/40 border border-emerald-500/30 hover:border-emerald-400 px-4 py-3 rounded text-emerald-400 hover:text-emerald-300 transition-all shadow-sm group"
                >
                  <span>3. Request formal Data Compliance Review</span>
                  <svg
                    className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M14 5l7 7m0 0l-7 7m7-7H3"
                    ></path>
                  </svg>
                </button>
              </div>
            </div>

            {/* Footer */}
            <div className="bg-gray-900/50 border-t border-gray-800 p-3 text-center text-[10px] text-gray-500 uppercase tracking-widest flex items-center justify-center gap-2">
              <svg className="w-3 h-3 text-emerald-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-6h2v6zm-1-6.8c-.66 0-1.2-.54-1.2-1.2s.54-1.2 1.2-1.2 1.2.54 1.2 1.2-.54 1.2-1.2 1.2z" />
              </svg>
              Logged internally by UphillSnowball Zero-Trust Architecture
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
