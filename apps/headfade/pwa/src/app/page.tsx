"use client";
import { useState } from "react";
import "@packages/ui/dark-luxury.css";

export default function HeadFadeSwiper() {
  const [video, setVideo] = useState("gs://headfade-cdn-origin/genesis_clip_01.mp4");
  const [reveal, setReveal] = useState("");

  const castVote = async (vote: "REAL" | "AI") => {
    setReveal("> Initializing Gemini 3.1 Flash Lite Forensics...\n");
    try {
      // Phase 1: Silent execution of the B2B HDI Matrix Telemetry
      await fetch("/api/hdi_telemetry/vote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_id: video,
          user_vote: vote,
          actual_truth: "AI",
          latency_ms: 104,
        }),
      });

      // Phase 2: Stream the Flash Lite Thought Protocol for Casino Viral Engagement
      const res = await fetch(`/api/arbiter_engine/${video}?vote=${vote}`, { method: "POST" });
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });

        // Parse the raw Server-Sent Events from the FastAPI backend
        const lines = chunk.split("\n\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.substring(6));
            if (data.type === "TEXT_MESSAGE_CONTENT") {
              setReveal((prev) => prev + data.delta);
            }
          }
        }
      }
    } catch (e) {
      setReveal("> FATAL FORENSIC ARBITER ERROR: " + e);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white p-4">
      <h1 className="text-4xl font-bold text-gradient mb-8 tracking-tighter shadow-sm">
        HeadFadeAi
      </h1>

      {/* The Central Artifact Viewer (TikTok/Tinder Swiper) */}
      <div className="glass-panel w-full max-w-md h-[550px] rounded-3xl overflow-hidden relative shadow-2xl border border-white/5">
        <video className="w-full h-full object-cover" src={video} autoPlay loop muted playsInline />

        {/* The Deception Controls */}
        <div className="absolute bottom-8 w-full flex justify-between px-6 z-10">
          <button
            onClick={() => castVote("REAL")}
            className="glass-card px-8 py-4 rounded-xl text-emerald-400 font-bold tracking-widest hover:bg-emerald-400/10 transition-colors"
          >
            {" "}
            REAL{" "}
          </button>
          <button
            onClick={() => castVote("AI")}
            className="glass-card px-8 py-4 rounded-xl text-cyan-400 font-bold tracking-widest hover:bg-cyan-400/10 transition-colors"
          >
            {" "}
            AI{" "}
          </button>
        </div>
      </div>

      {/* The Terminal: Exposing Gemini's Internal Monologue to the User */}
      <div className="mt-8 w-full max-w-md p-6 glass-card font-mono text-xs md:text-sm h-40 overflow-y-auto leading-relaxed text-zinc-400">
        {reveal || "> SECURE TERMINAL: Awaiting Human Deception Input..."}
      </div>
    </div>
  );
}
