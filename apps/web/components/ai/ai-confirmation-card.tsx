"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Sparkles, Check, X, ShieldAlert } from "lucide-react";

interface AIConfirmationCardProps {
  action: {
    id: string;
    action_type: string;
    proposed_changes: Record<string, any>;
    reasoning?: string;
  };
  onComplete?: () => void;
}

export function AIConfirmationCard({ action, onComplete }: AIConfirmationCardProps) {
  const queryClient = useQueryClient();

  const confirmMutation = useMutation({
    mutationFn: () => apiClient(`/api/v1/ai/actions/${action.id}/confirm`, { method: "POST" }),
    onSuccess: () => {
      toast.success("AI suggestion confirmed and applied!");
      queryClient.invalidateQueries();
      onComplete?.();
    },
  });

  const rejectMutation = useMutation({
    mutationFn: () => apiClient(`/api/v1/ai/actions/${action.id}/reject`, { method: "POST" }),
    onSuccess: () => {
      toast.info("AI suggestion discarded");
      queryClient.invalidateQueries();
      onComplete?.();
    },
  });

  return (
    <div className="p-3.5 rounded-xl bg-gradient-to-br from-violet-950/40 to-slate-900 border border-violet-500/30 space-y-2.5 text-xs shadow-lg">
      <div className="flex items-center gap-2 text-violet-400 font-semibold text-[11px]">
        <Sparkles className="w-3.5 h-3.5 animate-pulse" />
        <span>AI Proposed CRM Update (Requires Confirmation)</span>
      </div>

      {action.reasoning && (
        <p className="text-slate-300 text-[11px] bg-slate-950/50 p-2 rounded border border-slate-800/60 italic">
          "{action.reasoning}"
        </p>
      )}

      <div className="space-y-1">
        <span className="text-[10px] font-medium text-slate-500 uppercase">Proposed Changes:</span>
        <div className="bg-slate-950/80 p-2 rounded font-mono text-[10px] text-emerald-400 space-y-0.5">
          {Object.entries(action.proposed_changes).map(([k, v]) => (
            <div key={k} className="flex justify-between">
              <span className="text-slate-400">{k}:</span>
              <span>{String(v)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-2 pt-1">
        <button
          onClick={() => rejectMutation.mutate()}
          disabled={rejectMutation.isPending}
          className="flex items-center gap-1 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 text-xs font-medium"
        >
          <X className="w-3 h-3" /> Reject
        </button>
        <button
          onClick={() => confirmMutation.mutate()}
          disabled={confirmMutation.isPending}
          className="flex items-center gap-1 px-3 py-1 rounded bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium"
        >
          <Check className="w-3 h-3" /> Confirm & Apply
        </button>
      </div>
    </div>
  );
}
