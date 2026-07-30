"use client";

import { useState, useEffect, useRef } from "react";
import { Sparkles, Loader2 } from "lucide-react";

interface AIStreamingTextProps {
  /** SSE endpoint URL */
  endpoint: string;
  /** Request body */
  body: any;
  /** Auto-start on mount */
  autoStart?: boolean;
  /** Callback when streaming completes */
  onComplete?: (fullText: string) => void;
}

export function AIStreamingText({ endpoint, body, autoStart = true, onComplete }: AIStreamingTextProps) {
  const [text, setText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const startStreaming = async () => {
    setIsStreaming(true);
    setError(null);
    setText("");

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") continue;
            try {
              const parsed = JSON.parse(data);
              if (parsed.text) {
                fullText += parsed.text;
                setText(fullText);
                if (containerRef.current) {
                  containerRef.current.scrollTop = containerRef.current.scrollHeight;
                }
              }
            } catch {
              // Non-JSON SSE data, append as text
              fullText += data;
              setText(fullText);
            }
          }
        }
      }

      onComplete?.(fullText);
    } catch (err: any) {
      setError(err.message || "Streaming failed");
    } finally {
      setIsStreaming(false);
    }
  };

  useEffect(() => {
    if (autoStart) startStreaming();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="space-y-2">
      <div
        ref={containerRef}
        className="p-3 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 max-h-60 overflow-y-auto text-xs text-slate-700 dark:text-slate-300 leading-relaxed"
      >
        {error ? (
          <span className="text-red-400">{error}</span>
        ) : text ? (
          <span className="whitespace-pre-wrap">{text}</span>
        ) : isStreaming ? (
          <span className="flex items-center gap-2 text-slate-400">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Generating...</span>
          </span>
        ) : (
          <span className="text-slate-400">No output</span>
        )}
        {isStreaming && <span className="inline-block w-1.5 h-3 bg-violet-500 animate-pulse ml-0.5" />}
      </div>
      {!autoStart && !isStreaming && (
        <button
          onClick={startStreaming}
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-violet-600 text-white text-xs hover:bg-violet-500"
        >
          <Sparkles className="w-3 h-3" /> Generate
        </button>
      )}
    </div>
  );
}