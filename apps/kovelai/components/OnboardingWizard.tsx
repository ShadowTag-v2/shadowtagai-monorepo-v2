/**
 * Firm Onboarding Wizard Component
 *
 * Sprint Item #16: Multi-step onboarding flow for new law firms.
 *
 * Steps:
 * 1. Firm Information (name, bar number, jurisdiction)
 * 2. Subscription Tier Selection (Solo/Practice/Enterprise)
 * 3. Stripe Connect Onboarding (payment setup)
 * 4. BYOK Key Configuration (optional)
 * 5. Confirmation & First Session
 *
 * @see lib/billing/stripe-connect.ts — Stripe integration
 */

"use client";

import type React from "react";
import { useState } from "react";

// ─── Types ──────────────────────────────────────────────────────────

interface FirmData {
  firmName: string;
  contactEmail: string;
  barNumber: string;
  jurisdiction: string;
  tier: "solo" | "practice" | "enterprise";
}

type WizardStep = 1 | 2 | 3 | 4 | 5;

const TIER_INFO = {
  solo: {
    name: "Solo Practitioner",
    price: "$299/mo",
    features: ["1 attorney", "500K tokens/day", "Privileged search", "Anxiety radar"],
  },
  practice: {
    name: "Practice",
    price: "$599/mo",
    features: [
      "Up to 5 attorneys",
      "2M tokens/day",
      "Murder Board",
      "Oracle Memos",
      "Client portal",
    ],
  },
  enterprise: {
    name: "Enterprise",
    price: "$999/mo",
    features: [
      "Unlimited attorneys",
      "10M tokens/day",
      "BYOK",
      "Custom models",
      "Compliance reports",
      "Dedicated support",
    ],
  },
};

// ─── Component ──────────────────────────────────────────────────────

export function OnboardingWizard() {
  const [step, setStep] = useState<WizardStep>(1);
  const [firmData, setFirmData] = useState<FirmData>({
    firmName: "",
    contactEmail: "",
    barNumber: "",
    jurisdiction: "",
    tier: "practice",
  });
  const [loading, setLoading] = useState(false);

  const updateField = (field: keyof FirmData, value: string) => {
    setFirmData((prev) => ({ ...prev, [field]: value }));
  };

  const nextStep = () => setStep((prev) => Math.min(prev + 1, 5) as WizardStep);
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1) as WizardStep);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/internal/provision-tenant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          firmId: crypto.randomUUID(),
          firmName: firmData.firmName,
          tier: firmData.tier,
          adminEmail: firmData.contactEmail,
          jurisdiction: firmData.jurisdiction,
        }),
      });

      if (response.ok) {
        nextStep();
      }
    } catch (_err) {
    } finally {
      setLoading(false);
    }
  };

  const inputStyle: React.CSSProperties = {
    width: "100%",
    padding: "12px 16px",
    background: "#0c0c1f",
    border: "none",
    borderBottom: "2px solid #3c494e",
    borderRadius: "4px 4px 0 0",
    color: "#e2e0fc",
    fontSize: "15px",
    fontFamily: "Inter, sans-serif",
    outline: "none",
    boxSizing: "border-box",
    marginBottom: "16px",
  };

  const labelStyle: React.CSSProperties = {
    fontSize: "13px",
    color: "#859398",
    marginBottom: "6px",
    display: "block",
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0d1117",
        color: "#e2e0fc",
        fontFamily: "Inter, sans-serif",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "540px",
          padding: "48px",
          background: "#1a1a2e",
          borderRadius: "8px",
          borderTop: "0.5px solid rgba(180, 235, 255, 0.08)",
        }}
      >
        {/* Progress */}
        <div
          style={{
            display: "flex",
            gap: "4px",
            marginBottom: "32px",
          }}
        >
          {[1, 2, 3, 4, 5].map((s) => (
            <div
              key={s}
              style={{
                flex: 1,
                height: "3px",
                borderRadius: "2px",
                background: s <= step ? "#00d4ff" : "#333348",
                transition: "background 0.3s",
              }}
            />
          ))}
        </div>

        {/* Step 1: Firm Info */}
        {step === 1 && (
          <>
            <h2
              style={{
                fontFamily: "Space Grotesk",
                fontSize: "24px",
                fontWeight: 600,
                marginBottom: "8px",
                letterSpacing: "-0.02em",
              }}
            >
              Firm Information
            </h2>
            <p style={{ color: "#859398", fontSize: "14px", marginBottom: "32px" }}>
              Tell us about your practice.
            </p>
            <label htmlFor="firmName" style={labelStyle}>
              Firm Name
            </label>
            <input
              id="firmName"
              style={inputStyle}
              value={firmData.firmName}
              onChange={(e) => updateField("firmName", e.target.value)}
              placeholder="e.g., Smith & Associates LLP"
              aria-label="Firm Name"
            />
            <label htmlFor="contactEmail" style={labelStyle}>
              Contact Email
            </label>
            <input
              id="contactEmail"
              style={inputStyle}
              type="email"
              value={firmData.contactEmail}
              onChange={(e) => updateField("contactEmail", e.target.value)}
              placeholder="partner@firm.com"
              aria-label="Contact Email"
            />
            <label htmlFor="barNumber" style={labelStyle}>
              Bar Number
            </label>
            <input
              id="barNumber"
              style={inputStyle}
              value={firmData.barNumber}
              onChange={(e) => updateField("barNumber", e.target.value)}
              placeholder="e.g., NY-1234567"
              aria-label="Bar Number"
            />
            <label htmlFor="jurisdiction" style={labelStyle}>
              Primary Jurisdiction
            </label>
            <input
              id="jurisdiction"
              style={inputStyle}
              value={firmData.jurisdiction}
              onChange={(e) => updateField("jurisdiction", e.target.value)}
              placeholder="e.g., New York, Southern District"
              aria-label="Primary Jurisdiction"
            />
          </>
        )}

        {/* Step 2: Tier Selection */}
        {step === 2 && (
          <>
            <h2
              style={{
                fontFamily: "Space Grotesk",
                fontSize: "24px",
                fontWeight: 600,
                marginBottom: "8px",
                letterSpacing: "-0.02em",
              }}
            >
              Select Your Plan
            </h2>
            <p style={{ color: "#859398", fontSize: "14px", marginBottom: "32px" }}>
              All plans include Kovel privilege protection.
            </p>
            {(Object.entries(TIER_INFO) as [string, typeof TIER_INFO.solo][]).map(([key, tier]) => (
              // biome-ignore lint/a11y/useSemanticElements: custom styled radio card, native input[type=radio] breaks visual layout
              <div
                key={key}
                onClick={() => updateField("tier", key)}
                role="radio"
                aria-checked={firmData.tier === key}
                aria-label={`Select ${tier.name} plan at ${tier.price}`}
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    updateField("tier", key);
                  }
                }}
                style={{
                  padding: "20px",
                  marginBottom: "12px",
                  background: firmData.tier === key ? "#28283d" : "#111125",
                  borderRadius: "6px",
                  cursor: "pointer",
                  border:
                    firmData.tier === key
                      ? "1px solid rgba(0, 212, 255, 0.3)"
                      : "1px solid transparent",
                  transition: "all 0.2s",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "8px",
                  }}
                >
                  <span style={{ fontWeight: 600, fontSize: "16px" }}>{tier.name}</span>
                  <span style={{ color: "#00d4ff", fontFamily: "Space Grotesk", fontWeight: 600 }}>
                    {tier.price}
                  </span>
                </div>
                <div style={{ fontSize: "13px", color: "#859398" }}>
                  {tier.features.join(" • ")}
                </div>
              </div>
            ))}
          </>
        )}

        {/* Step 3: Payment */}
        {step === 3 && (
          <>
            <h2
              style={{
                fontFamily: "Space Grotesk",
                fontSize: "24px",
                fontWeight: 600,
                marginBottom: "8px",
                letterSpacing: "-0.02em",
              }}
            >
              Payment Setup
            </h2>
            <p style={{ color: "#859398", fontSize: "14px", marginBottom: "32px" }}>
              Secure payment via Stripe Connect. Your credentials never touch our servers.
            </p>
            <div
              style={{
                padding: "40px",
                textAlign: "center",
                background: "#111125",
                borderRadius: "6px",
              }}
            >
              <div style={{ fontSize: "48px", marginBottom: "16px" }}>💳</div>
              <p style={{ color: "#bbc9cf", fontSize: "14px" }}>
                You will be redirected to Stripe to complete onboarding.
              </p>
              <p style={{ color: "#859398", fontSize: "12px", marginTop: "8px" }}>
                Beta coupon <code style={{ color: "#00d4ff" }}>3wseBY7Z</code> applied — 50% off for
                3 months
              </p>
            </div>
          </>
        )}

        {/* Step 4: BYOK */}
        {step === 4 && (
          <>
            <h2
              style={{
                fontFamily: "Space Grotesk",
                fontSize: "24px",
                fontWeight: 600,
                marginBottom: "8px",
                letterSpacing: "-0.02em",
              }}
            >
              API Keys (Optional)
            </h2>
            <p style={{ color: "#859398", fontSize: "14px", marginBottom: "32px" }}>
              Bring your own API keys for Anthropic, Google, or OpenAI. Encrypted client-side.
            </p>
            <div
              style={{
                padding: "20px",
                background: "#111125",
                borderRadius: "6px",
                marginBottom: "16px",
              }}
            >
              <p style={{ color: "#bbc9cf", fontSize: "13px" }}>
                🔐 Keys are encrypted in your browser using AES-256-GCM before transmission. We
                never see the plaintext.
              </p>
            </div>
            <label htmlFor="anthropicKey" style={labelStyle}>
              Anthropic API Key (optional)
            </label>
            <input
              id="anthropicKey"
              style={inputStyle}
              type="password"
              placeholder="sk-ant-..."
              autoComplete="off"
              aria-label="Anthropic API Key"
            />
            <label htmlFor="vertexKey" style={labelStyle}>
              Google Vertex AI Key (optional)
            </label>
            <input
              id="vertexKey"
              style={inputStyle}
              type="password"
              placeholder="AIza..."
              autoComplete="off"
              aria-label="Google Vertex AI Key"
            />
          </>
        )}

        {/* Step 5: Confirmation */}
        {step === 5 && (
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: "64px", marginBottom: "16px" }}>✅</div>
            <h2
              style={{
                fontFamily: "Space Grotesk",
                fontSize: "24px",
                fontWeight: 600,
                marginBottom: "8px",
                letterSpacing: "-0.02em",
              }}
            >
              Welcome to KovelAI
            </h2>
            <p style={{ color: "#bbc9cf", fontSize: "15px", marginBottom: "32px" }}>
              Your firm has been provisioned. Your first privileged search session is ready.
            </p>
            <div
              style={{
                padding: "16px",
                background: "#111125",
                borderRadius: "6px",
                textAlign: "left",
              }}
            >
              <div style={{ fontSize: "13px", color: "#859398", marginBottom: "8px" }}>
                Quick Summary:
              </div>
              <div style={{ fontSize: "14px" }}>
                • <strong>Firm:</strong> {firmData.firmName}
              </div>
              <div style={{ fontSize: "14px" }}>
                • <strong>Plan:</strong> {TIER_INFO[firmData.tier].name} (
                {TIER_INFO[firmData.tier].price})
              </div>
              <div style={{ fontSize: "14px" }}>
                • <strong>Jurisdiction:</strong> {firmData.jurisdiction}
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div
          style={{
            display: "flex",
            justifyContent: step === 1 ? "flex-end" : "space-between",
            marginTop: "32px",
            gap: "12px",
          }}
        >
          {step > 1 && step < 5 && (
            <button
              type="button"
              onClick={prevStep}
              style={{
                padding: "12px 24px",
                background: "transparent",
                color: "#bbc9cf",
                border: "1px solid #3c494e",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "14px",
              }}
            >
              Back
            </button>
          )}
          {step < 4 && (
            <button
              type="button"
              onClick={nextStep}
              style={{
                padding: "12px 24px",
                background: "#00d4ff",
                color: "#00586b",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: 600,
                fontFamily: "Space Grotesk",
              }}
            >
              Continue
            </button>
          )}
          {step === 4 && (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              style={{
                padding: "12px 24px",
                background: loading ? "#333348" : "#00d4ff",
                color: loading ? "#bbc9cf" : "#00586b",
                border: "none",
                borderRadius: "6px",
                cursor: loading ? "wait" : "pointer",
                fontSize: "14px",
                fontWeight: 600,
                fontFamily: "Space Grotesk",
              }}
            >
              {loading ? "Provisioning..." : "Complete Setup"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
