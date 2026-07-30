"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Sparkles, Loader2, X } from "lucide-react";

interface AIInlineActionsProps {
  /** The context type for the AI action, e.g. "crm", "project", "finance", "knowledge" */
  context: string;
  /** The entity ID or page identifier */
  entityId?: string;
  /** Optional text content to operate on */
  text?: string;
  /** Callback when AI produces a result */
  onResult?: (result: any) => void;
  /** Available actions — defaults to text actions */
  actions?: string[];
}

const DEFAULT_TEXT_ACTIONS = ["Summarize", "Improve", "Translate", "Expand", "Change Tone"];
const DEFAULT_LIST_ACTIONS = ["Analyze Trends", "Suggest Priorities"];
const DEFAULT_RECORD_ACTIONS = ["Predict Close Date", "Suggest Upsell"];
const DEFAULT_PROJECT_ACTIONS = ["Sprint Summary", "Risk Detection"];
const DEFAULT_DASHBOARD_ACTIONS = ["Explain This Chart", "What Should I Focus On?"];

export function AIInlineActions({
  context,
  entityId,
  text,
  onResult,
  actions,
}: AIInlineActionsProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [showResult, setShowResult] = useState(false);

  const getActions = (): string[] => {
    if (actions) return actions;
    switch (context) {
      case "list": return DEFAULT_LIST_ACTIONS;
      case "record": return DEFAULT_RECORD_ACTIONS;
      case "project": return DEFAULT_PROJECT_ACTIONS;
      case "dashboard": return DEFAULT_DASHBOARD_ACTIONS;
      default: return DEFAULT_TEXT_ACTIONS;
    }
  };

  const handleAction = async (action: string) => {
    setLoading(action);
    try {
      const res = await apiClient("/api/v1/ai/sales/summarize", {
        method: "POST",
        body: JSON.stringify({
          context,
          entity_id: entityId,
          action: action.toLowerCase().replace(/\s+/g, "_"),
          text: text || "",
        }),
      });
      setResult({ action, data: res });
      setShowResult(true);
      onResult?.(res);
    } catch (err: any) {
      setResult({ action, error: err.message || "AI request failed" });
      setShowResult(true);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="relative inline-flex items-center gap-1">
      {getActions().map((action) => (
        <button
          key={action}
          onClick={() => handleAction(action)}
          disabled={loading !== null}
          className="flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium text-slate-500 hover:text-violet-500 hover:bg-violet-500/10 transition disabled:opacity-50"
          title={`AI: ${action}`}
        >
          {loading === action ? (
            <Loader2 className="w-3 h-3 animate-spin" />
          ) : (
            <Sparkles className="w-3 h-3" />
          )}
          {action}
        </button>
      ))}

      {/* Result Popover */}
      {showResult && result && (
        <div className="absolute top-full right-0 mt-1 z-50 w-80 p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-violet-500" />
              {result.action}
            </span>
            <button onClick={() => setShowResult(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
          {result.error ? (
            <p className="text-[11px] text-red-400">{result.error}</p>
          ) : (
            <pre className="whitespace-pre-wrap text-[11px] text-slate-600 dark:text-slate-300 font-sans leading-relaxed max-h-60 overflow-y-auto">
              {typeof result.data === "string" ? result.data : JSON.stringify(result.data, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}