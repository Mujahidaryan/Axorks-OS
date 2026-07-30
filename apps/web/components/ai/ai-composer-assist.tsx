"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Sparkles, Loader2, Wand2, RotateCcw, Check } from "lucide-react";

interface AIComposerAssistProps {
  /** Initial text value */
  initialValue?: string;
  /** Context for AI — e.g. "email", "note", "proposal_section" */
  context?: string;
  /** Callback when text is accepted */
  onAccept?: (text: string) => void;
  /** Placeholder text */
  placeholder?: string;
}

export function AIComposerAssist({
  initialValue = "",
  context = "general",
  onAccept,
  placeholder = "Write something or use AI to help...",
}: AIComposerAssistProps) {
  const [text, setText] = useState(initialValue);
  const [loading, setLoading] = useState<string | null>(null);
  const [showActions, setShowActions] = useState(false);

  const runAI = async (action: string) => {
    setLoading(action);
    try {
      const res = await apiClient("/api/v1/ai/sales/summarize", {
        method: "POST",
        body: JSON.stringify({
          context,
          action,
          text: text || "",
        }),
      });
      const resultText = typeof res === "string" ? res : res?.summary || res?.text || JSON.stringify(res);
      setText(resultText);
    } catch (err) {
      // Silently fail — AI is non-blocking
    } finally {
      setLoading(null);
    }
  };

  const actions = [
    { label: "Rewrite", icon: Wand2, action: "rewrite" },
    { label: "Improve", icon: Sparkles, action: "improve" },
    { label: "Expand", icon: Sparkles, action: "expand" },
    { label: "Formal Tone", icon: Sparkles, action: "formal_tone" },
    { label: "Friendly Tone", icon: Sparkles, action: "friendly_tone" },
  ];

  return (
    <div className="relative">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={placeholder}
        rows={4}
        onFocus={() => setShowActions(true)}
        className="w-full px-3 py-2 pr-10 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white resize-y"
      />
      {/* AI Actions */}
      {showActions && (
        <div className="absolute top-1 right-1 flex flex-col gap-0.5 bg-white dark:bg-slate-900 rounded-md border border-slate-200 dark:border-slate-800 shadow-sm p-1">
          {actions.map((a) => (
            <button
              key={a.action}
              onClick={() => runAI(a.action)}
              disabled={loading !== null}
              className="flex items-center gap-1.5 px-2 py-1 rounded text-[10px] text-slate-500 hover:text-violet-500 hover:bg-violet-500/10 transition disabled:opacity-50 whitespace-nowrap"
            >
              {loading === a.action ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <a.icon className="w-3 h-3" />
              )}
              {a.label}
            </button>
          ))}
          {text !== initialValue && (
            <>
              <div className="h-px bg-slate-200 dark:bg-slate-800 my-0.5" />
              <button
                onClick={() => setText(initialValue)}
                className="flex items-center gap-1.5 px-2 py-1 rounded text-[10px] text-slate-500 hover:text-amber-500 hover:bg-amber-500/10 transition"
              >
                <RotateCcw className="w-3 h-3" /> Revert
              </button>
              <button
                onClick={() => {
                  onAccept?.(text);
                  setShowActions(false);
                }}
                className="flex items-center gap-1.5 px-2 py-1 rounded text-[10px] text-slate-500 hover:text-green-500 hover:bg-green-500/10 transition"
              >
                <Check className="w-3 h-3" /> Accept
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}