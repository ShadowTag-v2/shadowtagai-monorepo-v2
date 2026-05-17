"use client";

import { useEffect, useRef } from "react";

import "./IsolatedAnalytics.css";

interface IsolatedAnalyticsProps {
  writeKey: string;
  cdnHost?: string;
  backendUrl?: string; // e.g., "http://localhost:8080"
}

export function IsolatedAnalytics({
  writeKey,
  cdnHost,
  backendUrl = "http://localhost:8080",
}: IsolatedAnalyticsProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Initialize analytics when iframe reports ready
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Security check: typically verify event.origin, but for this dev setup
      // with potentially varying ports (3000 vs 8080 vs 8000), we'll be permissive
      // or match the backendUrl domain.

      // Filter only for our isolated-segment messages
      if (event.data?.source !== "isolated-segment") return;

      if (event.data.type === "iframe_ready") {
        console.log("[Analytics] Iframe ready -> initializing");

        // Send init command
        iframeRef.current?.contentWindow?.postMessage(
          {
            target: "isolated-segment",
            type: "init",
            writeKey,
            cdnHost,
          },
          "*",
        );
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [writeKey, cdnHost]);

  return (
    <iframe
      ref={iframeRef}
      src={`${backendUrl}/public/segment_isolated.html`}
      title="Analytics"
      className="isolated-analytics-iframe"
      aria-hidden="true"
    />
  );
}
