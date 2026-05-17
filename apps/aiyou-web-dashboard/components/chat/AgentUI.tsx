import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_BASE_URL } from "../../src/config";

export default function AgentUI({ workspaceId }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);
  const [chatInput, setChatInput] = useState("");
  const [isChatting, setIsChatting] = useState(false);

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (!files || files.length === 0) return;

    const token = typeof window !== "undefined" ? localStorage.getItem("ShadowTag-v2_token") : null;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", files[0]);

      const response = await fetch(`${API_BASE_URL}/workspaces/${workspaceId}/knowledge/upload`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });

      if (!response.ok) throw new Error("Ingestion failed.");
      const result = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "system", content: `**✅ SYSTEM OMEGA RAG INGESTION:**\n\n${result.message}` },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setChatInput("");
    setMessages((prev) => [...prev, { role: "user", content: `**User:** ${userMsg}` }]);
    setIsChatting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/agents/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workspace_id: workspaceId || "default",
          agent_id: "agent-1",
          message: userMsg,
        }),
      });
      const result = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: `**Agent Omega:**\n\n${result.reply}` },
      ]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "system", content: `**❌ ERROR:** ${err.message}` }]);
    } finally {
      setIsChatting(false);
    }
  };

  return (
    <div className="flex flex-col h-full min-h-[500px] w-full bg-[#0A0B12] text-white p-4 rounded-xl border border-gray-800 shadow-2xl">
      <div
        className="flex-1 overflow-y-auto space-y-4 mb-4"
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        {isDragging ? (
          <div className="border-2 border-dashed border-emerald-500 rounded-lg p-10 text-center text-emerald-400 bg-emerald-900/20 h-full flex items-center justify-center">
            <h3>Drop documents here for LanceDB Autonomous RAG Ingestion</h3>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-gray-500 text-center mt-10">
            Drag .txt files to ingest data, or chat below.
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={`p-4 rounded-lg bg-gray-900/50 border border-gray-800 ${msg.role === "user" ? "border-l-4 border-l-blue-500" : "border-l-4 border-l-emerald-500"}`}
            >
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  img: ({ node, ...props }) => {
                    // Fix absolute pathing by injecting the API proxy explicitly
                    const fullSrc = props.src?.startsWith("/")
                      ? `${API_BASE_URL}${props.src}`
                      : props.src;
                    return (
                      <img
                        src={fullSrc}
                        alt={props.alt}
                        className="rounded-xl shadow-lg border border-gray-700 max-w-full my-4"
                      />
                    );
                  },
                }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          ))
        )}
      </div>

      {isUploading && (
        <p className="text-emerald-400 animate-pulse text-sm mb-2">
          Uploading vector matrices chunk to LanceDB...
        </p>
      )}
      {error && <p className="text-red-500 text-sm mb-2">{error}</p>}

      <form onSubmit={handleChat} className="flex gap-2">
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          disabled={isChatting}
          placeholder="Type 'generate an image of a dog' or ask about your data..."
          className="flex-1 bg-[#1A1B23] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-emerald-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isChatting}
          className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 px-6 rounded-lg transition-colors disabled:opacity-50"
        >
          {isChatting ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}
