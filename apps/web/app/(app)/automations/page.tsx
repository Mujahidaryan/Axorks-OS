"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Zap, Plus, Play, Pause, Trash2, Activity, ArrowRight, ChevronRight } from "lucide-react";

const TRIGGER_EVENTS = [
  "lead.created", "lead.updated", "lead.scored",
  "deal.created", "deal.won", "deal.lost",
  "project.created", "project.completed",
  "invoice.created", "invoice.paid",
  "proposal.sent", "proposal.accepted",
];

const ACTION_TYPES = [
  { type: "assign", label: "Assign" },
  { type: "send_email", label: "Send Email" },
  { type: "create_task", label: "Create Task" },
  { type: "update_field", label: "Update Field" },
  { type: "webhook", label: "Webhook" },
  { type: "ai_generate", label: "AI Generate" },
  { type: "notify_slack", label: "Notify Slack" },
];

export default function AutomationsPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [triggerEvent, setTriggerEvent] = useState(TRIGGER_EVENTS[0]);
  const [actionType, setActionType] = useState("assign");
  const [activeTab, setActiveTab] = useState<"workflows" | "executions">("workflows");

  const { data: workflows = [] } = useQuery({
    queryKey: ["automation-workflows"],
    queryFn: () => apiClient("/api/v1/automation/workflows"),
  });

  const { data: executions = [] } = useQuery({
    queryKey: ["automation-executions"],
    queryFn: () => apiClient("/api/v1/automation/executions"),
  });

  const createWorkflow = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/automation/workflows", {
        method: "POST",
        body: JSON.stringify({
          name,
          description: description || undefined,
          triggers: { events: [triggerEvent] },
          actions: { steps: [{ type: actionType }] },
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automation-workflows"] });
      toast.success("Workflow created!");
      setShowCreate(false);
      setName("");
      setDescription("");
    },
  });

  const toggleWorkflow = useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      apiClient(`/api/v1/automation/workflows/${id}/toggle?enabled=${enabled}`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automation-workflows"] });
      toast.success("Workflow updated");
    },
  });

  const deleteWorkflow = useMutation({
    mutationFn: (id: string) => apiClient(`/api/v1/automation/workflows/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automation-workflows"] });
      toast.success("Workflow deleted");
    },
  });

  const EXEC_STATUS_COLORS: Record<string, string> = {
    success: "bg-green-500/10 text-green-400",
    failed: "bg-red-500/10 text-red-400",
    running: "bg-blue-500/10 text-blue-400",
    skipped: "bg-slate-500/10 text-slate-400",
    pending: "bg-amber-500/10 text-amber-400",
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Automations</h1>
          <p className="text-xs text-slate-500 mt-0.5">Visual no-code automation — trigger → condition → action</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition"
        >
          <Plus className="w-3.5 h-3.5" /> New Workflow
        </button>
      </div>

      {/* Create Workflow */}
      {showCreate && (
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 max-w-lg space-y-3">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Create Workflow</h2>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Workflow name" className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white" />
          <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description (optional)" className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white" />
          <div className="space-y-2">
            <label className="text-[10px] uppercase tracking-wide text-slate-500 font-medium">When this happens (Trigger)</label>
            <select value={triggerEvent} onChange={(e) => setTriggerEvent(e.target.value)} className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white">
              {TRIGGER_EVENTS.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="flex items-center justify-center py-2">
            <ArrowRight className="w-4 h-4 text-slate-400" />
          </div>
          <div className="space-y-2">
            <label className="text-[10px] uppercase tracking-wide text-slate-500 font-medium">Do this (Action)</label>
            <select value={actionType} onChange={(e) => setActionType(e.target.value)} className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white">
              {ACTION_TYPES.map((a) => <option key={a.type} value={a.type}>{a.label}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowCreate(false)} className="px-4 py-1.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 text-xs">Cancel</button>
            <button onClick={() => createWorkflow.mutate()} disabled={!name.trim()} className="px-4 py-1.5 rounded bg-violet-600 text-white text-xs disabled:opacity-50">Create</button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800">
        <button onClick={() => setActiveTab("workflows")} className={`px-4 py-2 text-xs font-medium border-b-2 transition ${activeTab === "workflows" ? "border-violet-600 text-violet-600" : "border-transparent text-slate-500"}`}>Workflows ({workflows.length})</button>
        <button onClick={() => setActiveTab("executions")} className={`px-4 py-2 text-xs font-medium border-b-2 transition ${activeTab === "executions" ? "border-violet-600 text-violet-600" : "border-transparent text-slate-500"}`}>Execution Log ({executions.length})</button>
      </div>

      {/* Workflows */}
      {activeTab === "workflows" && (
        <div className="space-y-2">
          {workflows.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">No workflows yet. Create your first automation.</div>
          ) : (
            workflows.map((wf: any) => (
              <div key={wf.id} className="p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${wf.enabled ? "bg-violet-500/10" : "bg-slate-500/10"}`}>
                      <Zap className={`w-4 h-4 ${wf.enabled ? "text-violet-500" : "text-slate-400"}`} />
                    </div>
                    <div>
                      <span className="font-medium text-slate-800 dark:text-slate-200 text-xs block">{wf.name}</span>
                      {wf.description && <span className="text-[10px] text-slate-500">{wf.description}</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={() => toggleWorkflow.mutate({ id: wf.id, enabled: !wf.enabled })} className="p-1.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-violet-500">
                      {wf.enabled ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                    </button>
                    <button onClick={() => deleteWorkflow.mutate(wf.id)} className="p-1.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-red-500">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
                {/* Flow visualization */}
                <div className="flex items-center gap-2 mt-3 text-[10px] text-slate-500">
                  <span className="px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 font-mono">{(wf.triggers?.events || []).join(", ")}</span>
                  <ArrowRight className="w-3 h-3" />
                  <span className="px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 font-mono">{(wf.actions?.steps || []).map((s: any) => s.type).join(", ")}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Executions */}
      {activeTab === "executions" && (
        <div className="space-y-2">
          {executions.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">No executions logged yet.</div>
          ) : (
            executions.map((exec: any) => (
              <div key={exec.id} className="p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Activity className="w-4 h-4 text-slate-400" />
                    <div>
                      <span className="font-mono text-xs text-slate-700 dark:text-slate-300 block">{exec.trigger_event}</span>
                      <span className="text-[10px] text-slate-500">{new Date(exec.started_at).toLocaleString()}</span>
                    </div>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${EXEC_STATUS_COLORS[exec.status] || ""}`}>{exec.status}</span>
                </div>
                {exec.error && <p className="text-[10px] text-red-400 mt-2">{exec.error}</p>}
                {exec.steps_log?.steps && (
                  <div className="mt-2 space-y-1">
                    {exec.steps_log.steps.map((step: any, i: number) => (
                      <div key={i} className="text-[10px] text-slate-500 flex items-center gap-2">
                        <span className="font-mono">{step.step}</span>
                        {step.type && <span>· {step.type}</span>}
                        <span className="text-slate-400">· {step.result?.status || step.result?.reason || ""}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}