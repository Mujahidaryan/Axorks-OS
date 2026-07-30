"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { AIConfirmationCard } from "./ai-confirmation-card";
import {
  Sparkles, Send, HelpCircle, FileText, CheckSquare, DollarSign,
  TrendingUp, MessageSquare, Bot, AlertCircle,
} from "lucide-react";

interface AISalesPanelProps {
  entityType: string;
  entityId: string;
}

export function AISalesPanel({ entityType, entityId }: AISalesPanelProps) {
  const [prompt, setPrompt] = useState("");
  const [activeOutput, setActiveOutput] = useState<any>(null);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  // Fetch pending action confirmations
  const { data: pendingActions = [], refetch: refetchActions } = useQuery({
    queryKey: ["ai-pending-actions", entityType, entityId],
    queryFn: () => apiClient(`/api/v1/ai/actions?entity_type=${entityType}&entity_id=${entityId}`),
    enabled: !!entityId,
  });

  const runAIService = async (endpoint: string, payload: any, actionName: string) => {
    setLoadingAction(actionName);
    try {
      const res = await apiClient(`/api/v1/ai/sales/${endpoint}`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setActiveOutput({ title: actionName, data: res });
    } catch (e) {
      setActiveOutput({ title: actionName, error: "Failed to fetch AI response" });
    } finally {
      setLoadingAction(null);
    }
  };

  const triggerCRMUpdate = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/ai/sales/update-crm", {
        method: "POST",
        body: JSON.stringify({
          entity_type: entityType,
          entity_id: entityId,
          text_source: prompt || "Sales call discussion",
        }),
      }),
    onSuccess: () => {
      refetchActions();
      setPrompt("");
    },
  });

  return (
    <div className="w-80 border-l border-slate-800 bg-slate-950/60 backdrop-blur-md flex flex-col h-full shrink-0">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3.5 border-b border-slate-800 bg-violet-950/20">
        <Sparkles className="w-4 h-4 text-violet-400" />
        <span className="text-xs font-bold text-slate-200">AI Sales Copilot</span>
      </div>

      {/* Content Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Pending Confirmations Section */}
        {pendingActions.length > 0 && (
          <div className="space-y-2">
            <span className="text-[10px] font-semibold text-amber-400 uppercase tracking-wider">Pending Action Confirmations</span>
            {pendingActions.map((a: any) => (
              <AIConfirmationCard key={a.id} action={a} onComplete={refetchActions} />
            ))}
          </div>
        )}

        {/* Suggestion Chips */}
        <div className="space-y-1.5">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Contextual AI Actions</span>
          <div className="grid grid-cols-1 gap-1.5">
            <button
              onClick={() => runAIService("suggest-questions", { entity_type: entityType, entity_id: entityId }, "Discovery Questions")}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-violet-500/50 text-slate-300 text-xs text-left transition"
            >
              <HelpCircle className="w-3.5 h-3.5 text-cyan-400" /> Suggest Call Questions
            </button>

            <button
              onClick={() => runAIService("detect-requirements", { conversation_text: "Need RBAC, Postgres, and analytics" }, "Detected Requirements")}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-violet-500/50 text-slate-300 text-xs text-left transition"
            >
              <FileText className="w-3.5 h-3.5 text-violet-400" /> Extract Requirements
            </button>

            <button
              onClick={() => runAIService("estimate-budget", { requirements: ["RBAC", "Dashboard", "Postgres"] }, "Budget Estimate")}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-violet-500/50 text-slate-300 text-xs text-left transition"
            >
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Estimate Budget & Scope
            </button>

            <button
              onClick={() => runAIService("suggest-followup", { call_outcome: "positive", key_points: ["Demo presented", "Budget discussed"] }, "Follow-up Email")}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-violet-500/50 text-slate-300 text-xs text-left transition"
            >
              <MessageSquare className="w-3.5 h-3.5 text-amber-400" /> Draft Follow-up Email
            </button>
          </div>
        </div>

        {/* Response Display Box */}
        {loadingAction ? (
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-violet-400 animate-spin" />
            <span>Analyzing context via AI...</span>
          </div>
        ) : activeOutput && (
          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-semibold text-slate-200">{activeOutput.title}</span>
              <button onClick={() => setActiveOutput(null)} className="text-slate-500 hover:text-slate-300 text-[10px]">Close</button>
            </div>
            <pre className="whitespace-pre-wrap text-[11px] text-slate-300 font-sans leading-relaxed">
              {JSON.stringify(activeOutput.data, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Footer "Ask AI" Input */}
      <div className="p-3 border-t border-slate-800 bg-slate-950 space-y-2">
        <div className="flex gap-1.5">
          <input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask AI Sales Copilot..."
            className="flex-1 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs focus:outline-none focus:border-violet-500"
            onKeyDown={(e) => e.key === "Enter" && prompt && triggerCRMUpdate.mutate()}
          />
          <button
            onClick={() => triggerCRMUpdate.mutate()}
            disabled={!prompt.trim() || triggerCRMUpdate.isPending}
            className="px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
