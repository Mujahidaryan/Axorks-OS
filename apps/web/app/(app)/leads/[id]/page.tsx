"use client";

import { use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { AIScoreBadge } from "@/components/leads/ai-score-badge";
import { toast } from "sonner";
import Link from "next/link";
import { ArrowLeft, Sparkles, Building2, User, Globe, Mail, Phone, Calendar } from "lucide-react";

export default function LeadDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const queryClient = useQueryClient();

  const { data: lead, isLoading } = useQuery({
    queryKey: ["lead", id],
    queryFn: () => apiClient(`/api/v1/leads/${id}`),
  });

  const { data: scoreHistory = [] } = useQuery({
    queryKey: ["lead-score-history", id],
    queryFn: () => apiClient(`/api/v1/leads/${id}/score-history`),
  });

  const scoreMutation = useMutation({
    mutationFn: () => apiClient(`/api/v1/leads/${id}/score`, { method: "POST" }),
    onSuccess: (res) => {
      toast.success(`Score updated to ${res.lead.score}/100!`);
      queryClient.invalidateQueries({ queryKey: ["lead", id] });
      queryClient.invalidateQueries({ queryKey: ["lead-score-history", id] });
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to score lead");
    },
  });

  if (isLoading) {
    return <div className="text-center py-12 text-xs text-slate-400">Loading lead details...</div>;
  }

  if (!lead) {
    return <div className="text-center py-12 text-xs text-rose-500">Lead not found</div>;
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <div>
        <Link href="/leads" className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-100">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to leads
        </Link>
      </div>

      {/* Detail Header */}
      <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">
              {lead.business_name || "Untitled Business"}
            </h1>
            <AIScoreBadge score={lead.score} />
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-violet-500/10 text-violet-400 border border-violet-500/30">
              {lead.status}
            </span>
          </div>
          <p className="text-xs text-slate-400 flex items-center gap-3">
            <span>Source: <strong className="capitalize text-slate-200">{lead.source}</strong></span>
            <span>Industry: <strong className="text-slate-200">{lead.industry || "N/A"}</strong></span>
          </p>
        </div>

        <button
          onClick={() => scoreMutation.mutate()}
          disabled={scoreMutation.isPending}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs shadow-lg shadow-violet-600/20 transition disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          {scoreMutation.isPending ? "AI Scoring..." : "Score with AI"}
        </button>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="md:col-span-2 space-y-6">
          <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <h2 className="text-sm font-bold flex items-center gap-2 border-b border-slate-800 pb-2">
              <Building2 className="w-4 h-4 text-violet-400" /> Business Details
            </h2>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-slate-500 block">Website</span>
                <span className="font-medium text-slate-200">{lead.website || "—"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Company Size</span>
                <span className="font-medium text-slate-200">{lead.company_size || "—"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Country</span>
                <span className="font-medium text-slate-200">{lead.country || "—"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Revenue Range</span>
                <span className="font-medium text-slate-200">{lead.revenue_range || "—"}</span>
              </div>
            </div>
          </div>

          <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <h2 className="text-sm font-bold flex items-center gap-2 border-b border-slate-800 pb-2">
              <User className="w-4 h-4 text-cyan-400" /> Decision Maker
            </h2>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-slate-500 block">Name</span>
                <span className="font-medium text-slate-200">{lead.decision_maker_name || "—"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Title</span>
                <span className="font-medium text-slate-200">{lead.decision_maker_title || "—"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Email</span>
                <span className="font-medium text-slate-200">{lead.email || "—"}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Phone</span>
                <span className="font-medium text-slate-200">{lead.phone || "—"}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Score History Sidebar */}
        <div className="space-y-6">
          <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <h2 className="text-sm font-bold flex items-center gap-2 border-b border-slate-800 pb-2">
              <Sparkles className="w-4 h-4 text-amber-400" /> Score History
            </h2>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
              {scoreHistory.length === 0 ? (
                <p className="text-xs text-slate-500">No score history yet.</p>
              ) : (
                scoreHistory.map((item: any) => (
                  <div key={item.id} className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1 text-xs">
                    <div className="flex justify-between items-center font-semibold">
                      <span>Score: {item.new_score}</span>
                      <span className="text-[10px] text-slate-500 capitalize">{item.scored_by}</span>
                    </div>
                    <p className="text-[11px] text-slate-400">{item.reason}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
