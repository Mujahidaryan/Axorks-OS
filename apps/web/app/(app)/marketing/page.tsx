"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Megaphone, Plus, Calendar, Mail, TrendingUp, ChevronRight } from "lucide-react";

const CAMPAIGN_TYPES = ["email", "social", "ads", "content", "seo"];
const CAMPAIGN_STATUS_COLORS: Record<string, string> = {
  draft: "bg-slate-500/10 text-slate-400",
  active: "bg-green-500/10 text-green-400",
  paused: "bg-amber-500/10 text-amber-400",
  completed: "bg-blue-500/10 text-blue-400",
};

export default function MarketingPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [type, setType] = useState("email");
  const [goal, setGoal] = useState("");

  const { data: campaigns = [] } = useQuery({
    queryKey: ["marketing-campaigns"],
    queryFn: () => apiClient("/api/v1/marketing/campaigns"),
  });

  const { data: contentItems = [] } = useQuery({
    queryKey: ["marketing-content"],
    queryFn: () => apiClient("/api/v1/marketing/content"),
  });

  const { data: funnelStats } = useQuery({
    queryKey: ["marketing-funnel"],
    queryFn: () => apiClient("/api/v1/marketing/funnel-stats"),
  });

  const createCampaign = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/marketing/campaigns", {
        method: "POST",
        body: JSON.stringify({ name, type, goal: goal || undefined }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["marketing-campaigns"] });
      toast.success("Campaign created!");
      setShowCreate(false);
      setName("");
      setGoal("");
    },
  });

  const funnelStages = funnelStats ? Object.entries(funnelStats) : [];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Marketing</h1>
          <p className="text-xs text-slate-500 mt-0.5">Campaigns, content calendar, email marketing & funnels</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition"
        >
          <Plus className="w-3.5 h-3.5" /> New Campaign
        </button>
      </div>

      {/* Funnel Stats */}
      {funnelStages.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
          {funnelStages.map(([stage, count]: [string, any]) => (
            <div key={stage} className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <p className="text-[10px] uppercase tracking-wide text-slate-500 font-medium">{stage}</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{count}</p>
            </div>
          ))}
        </div>
      )}

      {/* Create Campaign */}
      {showCreate && (
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 max-w-md space-y-3">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Create Campaign</h2>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Campaign name"
            className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white"
          />
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white"
          >
            {CAMPAIGN_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <input
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Goal (optional)"
            className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white"
          />
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowCreate(false)} className="px-4 py-1.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 text-xs">Cancel</button>
            <button
              onClick={() => createCampaign.mutate()}
              disabled={!name.trim()}
              className="px-4 py-1.5 rounded bg-violet-600 text-white text-xs disabled:opacity-50"
            >
              Create
            </button>
          </div>
        </div>
      )}

      {/* Campaigns List */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-2">
          <Megaphone className="w-4 h-4" /> Campaigns
        </h2>
        <div className="space-y-2">
          {campaigns.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">
              No campaigns yet. Create your first campaign to get started.
            </div>
          ) : (
            campaigns.map((c: any) => (
              <div
                key={c.id}
                className="flex items-center justify-between p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-violet-500/40 transition cursor-pointer group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                    <Megaphone className="w-4 h-4 text-violet-500" />
                  </div>
                  <div>
                    <span className="font-medium text-slate-800 dark:text-slate-200 text-xs block">{c.name}</span>
                    <span className="text-[10px] text-slate-500">{c.type} · {c.goal || "No goal set"}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${CAMPAIGN_STATUS_COLORS[c.status] || ""}`}>
                    {c.status}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-violet-500 transition" />
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Content Calendar */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-2">
          <Calendar className="w-4 h-4" /> Content Calendar
        </h2>
        <div className="space-y-2">
          {contentItems.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">
              No content scheduled. Add content items to your calendar.
            </div>
          ) : (
            contentItems.map((item: any) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-3 rounded-lg bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-medium text-slate-700 dark:text-slate-300">{item.title}</span>
                  <span className="text-[10px] text-slate-500">{item.content_type} · {item.platform || "any"}</span>
                </div>
                <span className="text-[10px] text-slate-500">
                  {item.scheduled_at ? new Date(item.scheduled_at).toLocaleDateString() : "Unscheduled"}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}