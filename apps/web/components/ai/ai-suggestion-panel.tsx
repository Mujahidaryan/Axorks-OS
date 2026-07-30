"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Sparkles, X, ThumbsUp, ThumbsDown, Loader2 } from "lucide-react";

interface AISuggestionPanelProps {
  /** Context type — e.g. "crm", "project", "finance" */
  context: string;
  /** Entity ID for context */
  entityId?: string;
  /** Title for the panel */
  title?: string;
}

interface Suggestion {
  id: string;
  text: string;
  reasoning?: string;
  type: string;
  accepted?: boolean;
  dismissed?: boolean;
}

export function AISuggestionPanel({ context, entityId, title = "AI Insights" }: AISuggestionPanelProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(true);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const res = await apiClient("/api/v1/ai/sales/suggest-questions", {
        method: "POST",
        body: JSON.stringify({ context, entity_id: entityId }),
      });
      const items: Suggestion[] = Array.isArray(res)
        ? res.map((s: any, i: number) => ({
            id: `sug-${i}-${Date.now()}`,
            text: s.text || s.question || s.suggestion || String(s),
            reasoning: s.reasoning || s.reason,
            type: s.type || "insight",
          }))
        : [{
            id: `sug-${Date.now()}`,
            text: res.summary || res.text || JSON.stringify(res),
            reasoning: res.reasoning,
            type: "insight",
          }];
      setSuggestions(items);
      setExpanded(true);
    } catch {
      // Non-blocking — AI suggestions are optional
    } finally {
      setLoading(false);
    }
  };

  const acceptSuggestion = (id: string) => {
    setSuggestions((prev) => prev.map((s) => (s.id === id ? { ...s, accepted: true } : s)));
  };

  const dismissSuggestion = (id: string) => {
    setSuggestions((prev) => prev.map((s) => (s.id === id ? { ...s, dismissed: true } : s)));
  };

  const visibleSuggestions = suggestions.filter((s) => !s.dismissed);

  return (
    <div className="rounded-xl bg-violet-500/5 border border-violet-500/20 overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-2.5 cursor-pointer hover:bg-violet-500/10 transition"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-violet-500" />
          <span className="text-xs font-semibold text-violet-600 dark:text-violet-400">{title}</span>
          {visibleSuggestions.length > 0 && (
            <span className="px-1.5 py-0.5 rounded-full bg-violet-500/20 text-violet-500 text-[9px] font-bold">
              {visibleSuggestions.length}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              fetchSuggestions();
            }}
            disabled={loading}
            className="text-[10px] text-violet-500 hover:text-violet-400 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : "Refresh"}
          </button>
        </div>
      </div>

      {/* Suggestions */}
      {expanded && (
        <div className="px-4 pb-3 space-y-2">
          {visibleSuggestions.length === 0 && !loading ? (
            <p className="text-[10px] text-slate-500 py-2">
              Click "Refresh" to get AI insights for this {context}.
            </p>
          ) : (
            visibleSuggestions.map((sug) => (
              <div
                key={sug.id}
                className={`p-3 rounded-lg border transition ${
                  sug.accepted
                    ? "bg-green-500/5 border-green-500/20"
                    : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
                }`}
              >
                <p className="text-xs text-slate-700 dark:text-slate-300">{sug.text}</p>
                {sug.reasoning && (
                  <p className="text-[10px] text-slate-400 mt-1 italic">Reasoning: {sug.reasoning}</p>
                )}
                {!sug.accepted && (
                  <div className="flex items-center gap-2 mt-2">
                    <button
                      onClick={() => acceptSuggestion(sug.id)}
                      className="flex items-center gap-1 text-[10px] text-green-500 hover:text-green-400"
                    >
                      <ThumbsUp className="w-3 h-3" /> Accept
                    </button>
                    <button
                      onClick={() => dismissSuggestion(sug.id)}
                      className="flex items-center gap-1 text-[10px] text-slate-400 hover:text-red-400"
                    >
                      <ThumbsDown className="w-3 h-3" /> Dismiss
                    </button>
                  </div>
                )}
                {sug.accepted && (
                  <span className="text-[10px] text-green-500 flex items-center gap-1 mt-1">
                    <ThumbsUp className="w-3 h-3" /> Accepted
                  </span>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}