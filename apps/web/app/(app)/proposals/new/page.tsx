"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Sparkles, FileText, ArrowRight } from "lucide-react";

export default function NewProposalWizardPage() {
  const router = useRouter();
  const [proposalType, setProposalType] = useState("proposal");
  const [dealId, setDealId] = useState("");
  const [title, setTitle] = useState("");
  const [useAI, setUseAI] = useState(true);

  const { data: deals = [] } = useQuery({
    queryKey: ["deals-select"],
    queryFn: () => apiClient("/api/v1/deals").then((r: any) => r.data),
  });

  const generateProposal = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/proposals/generate", {
        method: "POST",
        body: JSON.stringify({
          proposal_type: proposalType,
          deal_id: dealId || null,
          additional_notes: title,
        }),
      }),
    onSuccess: (res: any) => {
      toast.success("AI Proposal generated!");
      router.push(`/proposals/${res.data.id}`);
    },
  });

  const createBlankProposal = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/proposals", {
        method: "POST",
        body: JSON.stringify({
          title: title || "New Proposal",
          type: proposalType,
          deal_id: dealId || null,
        }),
      }),
    onSuccess: (res: any) => {
      toast.success("Blank proposal created!");
      router.push(`/proposals/${res.data.id}`);
    },
  });

  const handleCreate = () => {
    if (useAI) {
      generateProposal.mutate();
    } else {
      createBlankProposal.mutate();
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-8 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">Create Document</h1>
        <p className="text-xs text-slate-500 mt-1">Generate a proposal, SOW, quotation, or technical proposal.</p>
      </div>

      <div className="space-y-4">
        {/* Document Type Selection */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-300">Document Type</label>
          <div className="grid grid-cols-2 gap-2">
            {[
              { id: "proposal", label: "Business Proposal" },
              { id: "sow", label: "Statement of Work (SOW)" },
              { id: "quotation", label: "Price Quotation" },
              { id: "contract", label: "Service Contract" },
              { id: "technical_proposal", label: "Technical Architecture Proposal" },
            ].map((t) => (
              <button
                key={t.id}
                onClick={() => setProposalType(t.id)}
                className={`p-3 rounded-xl border text-left text-xs font-medium transition ${
                  proposalType === t.id
                    ? "bg-violet-600/10 border-violet-500 text-violet-300"
                    : "bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Linked Deal */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-300">Link to Deal (Optional)</label>
          <select
            value={dealId}
            onChange={(e) => setDealId(e.target.value)}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
          >
            <option value="">None (Standalone Document)</option>
            {deals.map((d: any) => (
              <option key={d.id} value={d.id}>{d.title} ({d.currency || '$'}{d.value})</option>
            ))}
          </select>
        </div>

        {/* Title / Notes */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-300">Document Title or Project Notes</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Enterprise Cloud Platform Architecture & Delivery"
            className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs"
          />
        </div>

        {/* Generation Mode Toggle */}
        <div className="p-4 rounded-xl bg-violet-950/20 border border-violet-500/30 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-violet-400" />
            <div>
              <p className="text-xs font-semibold text-white">Auto-Generate with AI Copilot</p>
              <p className="text-[10px] text-slate-400">Pulls scope, architecture, pricing items, and timeline automatically.</p>
            </div>
          </div>
          <input
            type="checkbox"
            checked={useAI}
            onChange={(e) => setUseAI(e.target.checked)}
            className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-violet-600 focus:ring-violet-500"
          />
        </div>

        {/* Action Button */}
        <div className="pt-4 flex justify-end">
          <button
            onClick={handleCreate}
            disabled={generateProposal.isPending || createBlankProposal.isPending}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-semibold shadow-lg shadow-violet-600/30 transition disabled:opacity-50"
          >
            <span>{useAI ? "Generate Proposal with AI" : "Create Blank Document"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
