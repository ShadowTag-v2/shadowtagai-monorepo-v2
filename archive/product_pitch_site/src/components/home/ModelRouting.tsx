export function ModelRouting() {
  const models = [
    { name: "Gemini", provider: "Google", color: "#4285f4", speed: "42ms", specialty: "Multi-modal reasoning" },
    { name: "Claude", provider: "Anthropic", color: "#d89e6c", speed: "55ms", specialty: "Long-form analysis" },
    { name: "ChatGPT", provider: "OpenAI", color: "#10a37f", speed: "38ms", specialty: "General research" },
    { name: "Grok", provider: "xAI", color: "#e74c3c", speed: "31ms", specialty: "Real-time data" },
    { name: "Google Search", provider: "Google", color: "#34a853", speed: "28ms", specialty: "Source-grounded web search" },
    { name: "Google Translate", provider: "Google", color: "#fbbc04", speed: "15ms", specialty: "Multilingual legal translation" },
  ];

  return (
    <section className="section-container">
      <div className="text-center mb-16">
        <h2 className="section-title mb-4">
          Six Tools. <span className="gradient-text">One Portal.</span>
        </h2>
        <p className="section-subtitle mx-auto">
          LiteLLM proxy routes every query through ephemeral, sandbox-bound tokens.
          Tenant-billed. Zero master keys in sandbox.
        </p>
      </div>

      <div className="space-y-3">
        {models.map((model, i) => (
          <div
            key={model.name}
            className="glass-card p-5 flex items-center gap-6 group cursor-default"
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            {/* Model indicator */}
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-sm shrink-0"
              style={{ background: `${model.color}20`, border: `1px solid ${model.color}40` }}
            >
              {model.name[0]}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{model.name}</span>
                <span className="text-xs text-[#8b949e]">by {model.provider}</span>
              </div>
              <div className="text-xs text-[#8b949e] mt-0.5">{model.specialty}</div>
            </div>

            <div className="hidden sm:flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-[#8b949e]">P95 Latency</div>
                <div className="text-sm font-mono font-medium" style={{ color: model.color }}>
                  {model.speed}
                </div>
              </div>
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: model.color }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
