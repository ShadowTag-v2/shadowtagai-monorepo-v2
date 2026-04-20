'use client';

import React, { useEffect, useState } from 'react';

export default function CookieConsent() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Auto-open on first load if no consent found
    const consent = localStorage.getItem('eu-cookie-consent');
    if (!consent) {
      const timer = setTimeout(() => setIsOpen(true), 0);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('eu-cookie-consent', 'accepted');
    setIsOpen(false);
  };

  const handleDecline = () => {
    localStorage.setItem('eu-cookie-consent', 'declined');
    setIsOpen(false);
  };

  if (!isOpen) {
    return (
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        aria-label="Open Cookie Settings"
        className="fixed bottom-8 left-8 z-[110] h-12 w-12 bg-[#1b103c] rounded-full flex items-center justify-center text-white shadow-[0_4px_20px_rgba(0,0,0,0.5)] hover:scale-105 transition-transform border-2 border-white/20 group"
      >
        <div className="relative w-6 h-6">
          {/* Replicating the UserWay / Accessibility dots layout circled in the user's red pen markup */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1.5 h-1.5 bg-white rounded-full"></div>
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1.5 h-1.5 bg-white rounded-full"></div>
          <div className="absolute top-1/2 left-0 -translate-y-1/2 w-1.5 h-1.5 bg-white rounded-full"></div>
          <div className="absolute top-1/2 right-0 -translate-y-1/2 w-1.5 h-1.5 bg-white rounded-full"></div>
          <div className="absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2 w-2 h-2 bg-white rounded-full shadow-[0_0_4px_rgba(255,255,255,0.8)]"></div>
        </div>
      </button>
    );
  }

  return (
    <div className="fixed bottom-0 left-0 w-full z-[120] bg-[#402d73] border-t border-indigo-900/50 text-white p-6 shadow-2xl animate-in slide-in-from-bottom duration-300">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative">
        <button
          type="button"
          onClick={() => setIsOpen(false)}
          aria-label="Minimize Cookie Banner"
          className="absolute -top-2 right-0 md:top-0 text-white/70 hover:text-white transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <title>Minimize</title>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>

        <div className="flex-1 pr-10">
          <h3 className="text-xl font-bold mb-2 tracking-tight text-white drop-shadow-sm">
            This website uses cookies
          </h3>
          <p className="text-sm text-indigo-100 leading-relaxed mb-4">
            This website uses cookies to improve user experience. By using our website you consent
            to all cookies in accordance with our Cookie Policy.{' '}
            <a href="/cookie-policy" className="underline hover:text-white transition-colors">
              Read more
            </a>
          </p>

          <div className="flex flex-wrap items-center gap-6 mt-4">
            <label className="flex items-center gap-2 cursor-not-allowed opacity-80 group">
              <input
                type="checkbox"
                checked
                readOnly
                className="w-5 h-5 rounded text-[#402d73] bg-white border-white focus:ring-0"
              />
              <span className="text-xs font-bold tracking-widest text-white uppercase">
                STRICTLY NECESSARY
              </span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer group">
              <input
                type="checkbox"
                defaultChecked
                className="w-5 h-5 rounded text-[#402d73] bg-white border-white focus:ring-0"
              />
              <span className="text-xs font-bold tracking-widest text-white uppercase opacity-90 group-hover:opacity-100">
                PERFORMANCE
              </span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer group">
              <input
                type="checkbox"
                defaultChecked
                className="w-5 h-5 rounded text-[#402d73] bg-white border-white focus:ring-0"
              />
              <span className="text-xs font-bold tracking-widest text-white uppercase opacity-90 group-hover:opacity-100">
                TARGETING
              </span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer group">
              <input
                type="checkbox"
                defaultChecked
                className="w-5 h-5 rounded text-[#402d73] bg-white border-white focus:ring-0"
              />
              <span className="text-xs font-bold tracking-widest text-white uppercase opacity-90 group-hover:opacity-100">
                FUNCTIONALITY
              </span>
            </label>

            <button
              type="button"
              className="flex items-center gap-1.5 text-xs font-bold tracking-widest uppercase ml-2 text-indigo-200 hover:text-white transition-colors"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <title>Show Details</title>
                <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
                <path
                  fillRule="evenodd"
                  clipRule="evenodd"
                  d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 12a2 2 0 114 0 2 2 0 01-4 0z"
                />
              </svg>
              SHOW DETAILS
            </button>
          </div>
        </div>

        <div className="flex gap-4 shrink-0 flex-col sm:flex-row w-full md:w-auto mt-6 md:mt-0">
          <button
            type="button"
            onClick={handleAccept}
            className="bg-white text-[#402d73] font-bold text-xs tracking-[0.2em] uppercase px-8 py-3 rounded-sm hover:bg-gray-100 transition-colors whitespace-nowrap shadow-md hover:shadow-lg"
          >
            ACCEPT ALL
          </button>
          <button
            type="button"
            onClick={handleDecline}
            className="bg-white/20 text-white font-bold text-xs tracking-[0.2em] uppercase px-8 py-3 rounded-sm hover:bg-white/30 transition-colors whitespace-nowrap border border-white/20"
          >
            DECLINE ALL
          </button>
        </div>
      </div>
    </div>
  );
}
