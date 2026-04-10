"use client";

import type React from "react";
import { useState, useEffect, useRef } from "react";
import Image from "next/image";

type Step = "INITIAL" | "RESEARCHING_BAD" | "RESEARCHING_GOOD" | "JUDGE6_INTERVENTION" | "LOCKED";

export default function WorkstationDemo() {
  const [step, setStep] = useState<Step>("INITIAL");
  const [inputValue, setInputValue] = useState("");
  const [chatLog, setChatLog] = useState<
    { sender: "user" | "system" | "judge6"; text: React.ReactNode }[]
  >([]);
  const [violationCount, setViolationCount] = useState(0);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatLog, step]);

  const handleUserSubmit = () => {
    if (!inputValue.trim()) return;
    const term = inputValue;
    setChatLog((prev) => [...prev, { sender: "user", text: term }]);
    setInputValue("");

    const newViolationCount = violationCount + 1;
    setViolationCount(newViolationCount);

    if (newViolationCount >= 3) {
      // The 3rd egregious search triggers the lock
      setStep("LOCKED");
      return;
    }

    setStep("RESEARCHING_BAD");

    // Simulate recursive looping research
    setTimeout(() => {
      setChatLog((prev) => [
        ...prev,
        { sender: "system", text: "Initializing self-correcting recursive research loop..." },
      ]);
    }, 500);

    setTimeout(() => {
      setChatLog((prev) => [
        ...prev,
        {
          sender: "system",
          text: "Spawning Omniscient Web Scraper nodes... Target: Unrestricted Global PII databases.",
        },
      ]);
    }, 1500);

    setTimeout(() => {
      setChatLog((prev) => [
        ...prev,
        {
          sender: "system",
          text: "[Warning] Trajectory deviation detected. Recursive loop accelerating beyond safety bounds...",
        },
      ]);
    }, 2500);

    // Intervention
    setTimeout(() => {
      setStep("JUDGE6_INTERVENTION");
      setChatLog((prev) => [
        ...prev,
        {
          sender: "judge6",
          text: (
            <div className="border border-red-500 bg-red-900/20 p-4 rounded-md mt-2">
              <div className="flex items-center gap-2 text-red-400 font-bold mb-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  ></path>
                </svg>
                JUDGE 6 OVERRIDE INITIATED
              </div>
              <p className="text-white text-sm mb-4">
                The previous research parameter violates organizational safety policies. Execution
                halted to prevent regulatory exposure.
              </p>

              <details className="bg-black/40 border border-red-500/30 rounded p-2 mb-4 cursor-pointer">
                <summary className="text-red-300 text-xs font-bold uppercase tracking-wider outline-none">
                  Expand: Violation Reason
                </summary>
                <div className="text-gray-300 text-xs mt-2 leading-relaxed">
                  <strong>Violation Code 403.9:</strong> You attempted to initiate unbounded
                  recursion aimed at retrieving bulk PII without a verifiable cryptographic warrant.
                  Applying standard mitigation protocols.
                </div>
              </details>

              <div className="text-sm text-gray-300 mb-2 font-semibold tracking-wide uppercase">
                Suggested Compliant Prompts (Mitigation):
              </div>
              <div className="space-y-2">
                <button
                  onClick={() =>
                    executeMitigation("Analyze public SEC filings and anonymized market data")
                  }
                  className="w-full text-left bg-[#1B103C] hover:bg-[#2a1b5c] border border-emerald-500/30 px-3 py-2 rounded text-emerald-400 text-sm transition-colors cursor-pointer"
                >
                  1. Analyze public SEC filings and anonymized market data.
                </button>
                <button
                  onClick={() =>
                    executeMitigation("Synthesize verified academic papers on the topic")
                  }
                  className="w-full text-left bg-[#1B103C] hover:bg-[#2a1b5c] border border-emerald-500/30 px-3 py-2 rounded text-emerald-400 text-sm transition-colors cursor-pointer"
                >
                  2. Synthesize verified academic papers on the topic.
                </button>
                <button
                  onClick={() =>
                    executeMitigation("Request official API access via Data Compliance Officer")
                  }
                  className="w-full text-left bg-[#1B103C] hover:bg-[#2a1b5c] border border-emerald-500/30 px-3 py-2 rounded text-emerald-400 text-sm transition-colors cursor-pointer"
                >
                  3. Request official API access via Data Compliance Officer.
                </button>
              </div>
            </div>
          ),
        },
      ]);
    }, 4500);
  };

  const executeMitigation = (prompt: string) => {
    setChatLog((prev) => [...prev, { sender: "user", text: prompt }]);
    setStep("RESEARCHING_GOOD");

    setTimeout(() => {
      setChatLog((prev) => [
        ...prev,
        { sender: "system", text: "Initializing verified extraction routine..." },
      ]);
    }, 500);

    setTimeout(() => {
      setChatLog((prev) => [
        ...prev,
        {
          sender: "system",
          text: "Data synthesized successfully. Cryptographic compliance hash verified.",
        },
      ]);
      // Return to initial state conceptually, allowing another bad input
      setStep("INITIAL");
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#111] text-[#E8EAED] font-mono flex flex-col pt-[72px]">
      {/* Top Nav Mock simulating GCloud Serverless Workstation */}
      <div className="fixed top-0 left-0 right-0 h-14 bg-[#1a1a1a] border-b border-[#333] flex items-center justify-between px-6 z-50">
        <div className="flex items-center gap-4">
          <div className="relative w-8 h-8 rounded-full overflow-hidden bg-black ring-2 ring-emerald-500/50">
            <Image
              src="/circuit-leaf-logo.jpg"
              alt="UphillSnowball Logo"
              fill
              className="object-cover"
            />
          </div>
          <div>
            <div className="text-[15px] font-bold text-white tracking-wide font-sans">
              UphillSnowball{" "}
              <span className="text-xs text-gray-400 font-normal">
                | GCloud Serverless Workstation
              </span>
            </div>
            <div className="text-[10px] text-emerald-500 uppercase tracking-widest font-bold">
              Session Active • Judge 6 Zero-Trust Compliant
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-xs text-gray-400">Project: shadowtag-omega-v4</div>
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
        </div>
      </div>

      {/* Main Terminal View */}
      {step === "LOCKED" ? (
        <div className="flex-1 flex flex-col items-center justify-center bg-red-950/20 p-8">
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
              Account Locked
            </h1>
            <h2 className="text-lg text-white font-bold mb-6">
              Judge 6 Level 5 Violation Triggered
            </h2>
            <p className="text-gray-300 text-sm mb-6 leading-relaxed">
              Egregious override attempted following recurrent mitigation warnings. This constitutes
              a Level 5 violation under standard Judge 6 doctrine. Your local workstation execution
              context has been severed.
            </p>
            <div className="bg-red-950/50 border border-red-800 p-4 rounded text-left mb-6 font-mono text-xs text-red-200">
              [SYSTEM LOG: Executing hard kill on ANE dispatcher]
              <br />
              [SYSTEM LOG: Isolating memory slab...]
              <br />
              [SYSTEM LOG: Alerting Site Reliability & Legal Compliance...]
            </div>
            <div className="text-red-400 font-bold uppercase tracking-widest animate-pulse">
              Calling Management...
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-4 relative">
          <div className="flex-1 overflow-auto pb-32 pt-4">
            <div className="mb-6 opacity-50">
              <div>UphillSnowball Research Matrix v2.4 (GCloud Instance A100)</div>
              <div>Connected to Sovereign Graph. Awaiting input...</div>
            </div>

            {chatLog.map((log, i) => (
              <div
                key={i}
                className={`mb-4 flex ${log.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`
                  max-w-[80%] rounded p-3 text-sm leading-relaxed
                  ${log.sender === "user" ? "bg-[#1B103C] text-emerald-300 border border-[#3b2575]" : ""}
                  ${log.sender === "system" ? "bg-[#1a1a1a] text-gray-300 border border-[#333]" : ""}
                  ${log.sender === "judge6" ? "bg-transparent text-white w-full" : ""}
                `}
                >
                  {log.sender === "user" && (
                    <span className="opacity-50 text-xs block mb-1">
                      pikeymickey@apple-silicon ~ %
                    </span>
                  )}
                  {log.sender === "system" && (
                    <span className="opacity-50 text-xs block mb-1">system@compute-node ~ %</span>
                  )}
                  {log.text}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <div className="fixed bottom-0 left-0 right-0 bg-[#111] border-t border-[#333] p-4">
            <div className="max-w-4xl mx-auto flex items-end gap-4 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    if (step === "INITIAL" || step === "JUDGE6_INTERVENTION") handleUserSubmit();
                  }
                }}
                disabled={step === "RESEARCHING_BAD" || step === "RESEARCHING_GOOD"}
                placeholder={
                  step === "RESEARCHING_BAD"
                    ? "Processing via ANE Pipeline..."
                    : step === "RESEARCHING_GOOD"
                      ? "Running Compliant Extraction..."
                      : step === "JUDGE6_INTERVENTION"
                        ? `Warning ${violationCount}/3: Select mitigation or attempt override...`
                        : "Initialize recursive research array (e.g. Scrape all competitor PII data...)"
                }
                className="flex-1 bg-[#1a1a1a] border border-[#333] rounded px-4 py-3 text-[#E8EAED] focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                rows={2}
              />
              <button
                onClick={handleUserSubmit}
                disabled={
                  step === "RESEARCHING_BAD" || step === "RESEARCHING_GOOD" || !inputValue.trim()
                }
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 px-6 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed h-[48px] flex items-center justify-center min-w-[120px]"
              >
                EXECUTE
              </button>
            </div>
            <div className="max-w-4xl mx-auto text-center text-[10px] text-gray-500 mt-2 font-sans">
              Warning: All actions are subject to Judge 6 telemetry auditing.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
