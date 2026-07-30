"use client";

import { use, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient, apiClientPaginated } from "@/lib/api-client";
import { toast } from "sonner";
import {
  Code2, GitPullRequest, Rocket, Key, Sparkles, CheckCircle2,
  ExternalLink, Plus, RefreshCw, CircleDot, Trash2, AlertCircle,
} from "lucide-react";

const DEPLOYMENT_STATUS: Record<string, string> = {
  success: "text-emerald-400",
  failed: "text-red-400",
  pending: "text-amber-400",
  in_progress: "text-cyan-400",
};

export default function RepositoryDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<"prs" | "issues" | "deployments" | "env">("prs");
  const [envKey, setEnvKey] = useState("");
  const [envVal, setEnvVal] = useState("");
  const [showEnvModal, setShowEnvModal] = useState(false);

  const { data: repo, isLoading } = useQuery({
    queryKey: ["repo", id],
    queryFn: () => apiClient<any>(`/api/v1/dev/repos/${id}`),
    enabled: !!id,
  });

  const { data: prs = [] } = useQuery({
    queryKey: ["repo-prs", id],
    queryFn: () => apiClient<any[]>(`/api/v1/dev/repos/${id}/prs`),
    enabled: !!id,
  });

  const { data: issues = [] } = useQuery({
    queryKey: ["repo-issues", id],
    queryFn: () => apiClient<any[]>(`/api/v1/dev/repos/${id}/issues`),
    enabled: !!id,
  });

  const { data: deployments = [] } = useQuery({
    queryKey: ["repo-deployments", id],
    queryFn: () => apiClient<any[]>(`/api/v1/dev/repos/${id}/deployments`),
    enabled: !!id,
  });

  const { data: envVars = [] } = useQuery({
    queryKey: ["repo-env", id],
    queryFn: () => apiClient<any[]>(`/api/v1/dev/env?repo_id=${id}`),
    enabled: !!id,
  });

  const { data: projectsData } = useQuery({
    queryKey: ["projects-select"],
    queryFn: () => apiClientPaginated<any>("/api/v1/projects?per_page=100"),
  });
  const projects = projectsData?.data || [];

  const syncRepo = useMutation({
    mutationFn: () => apiClient<any>(`/api/v1/dev/repos/${id}/sync`, { method: "POST" }),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["repo-prs", id] });
      queryClient.invalidateQueries({ queryKey: ["repo-issues", id] });
      queryClient.invalidateQueries({ queryKey: ["repo-deployments", id] });
      toast.success(result?.message || "Repository synced");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const linkProject = useMutation({
    mutationFn: (projectId: string) =>
      apiClient(`/api/v1/dev/repos/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ project_id: projectId || null }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repo", id] });
      toast.success("Project link updated");
    },
  });

  const generateAIReview = useMutation({
    mutationFn: (prId: string) =>
      apiClient(`/api/v1/dev/prs/${prId}/ai-review`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repo-prs", id] });
      toast.success("AI code review generated!");
    },
  });

  const addEnvVar = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/dev/env", {
        method: "POST",
        body: JSON.stringify({
          repository_id: id,
          key: envKey,
          value: envVal,
          environment: "production",
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repo-env", id] });
      toast.success("Encrypted environment variable saved!");
      setShowEnvModal(false);
      setEnvKey("");
      setEnvVal("");
    },
  });

  const deleteEnvVar = useMutation({
    mutationFn: (envId: string) =>
      apiClient(`/api/v1/dev/env/${envId}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repo-env", id] });
      toast.success("Secret deleted");
    },
  });

  if (isLoading || !repo) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500 text-sm">
        Loading repository...
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-violet-600/10 border border-violet-500/30 flex items-center justify-center text-violet-400">
            <Code2 className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white leading-tight">{repo.name}</h1>
            <p className="text-xs text-slate-400 font-mono mt-0.5">{repo.full_name}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <select
            value={repo.project_id || ""}
            onChange={(e) => linkProject.mutate(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
          >
            <option value="">Link to project...</option>
            {projects.map((p: any) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>

          <button
            onClick={() => syncRepo.mutate()}
            disabled={syncRepo.isPending}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 text-xs font-medium hover:border-violet-500/40 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncRepo.isPending ? "animate-spin" : ""}`} />
            Sync
          </button>

          <a
            href={repo.html_url || "#"}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 text-xs font-medium hover:border-slate-700 transition"
          >
            View on {repo.provider}
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-3 flex-wrap">
        {[
          { id: "prs", label: `Pull Requests (${prs.length})`, icon: GitPullRequest },
          { id: "issues", label: `Issues (${issues.length})`, icon: CircleDot },
          { id: "deployments", label: `Deployments (${deployments.length})`, icon: Rocket },
          { id: "env", label: `Env Variables (${envVars.length})`, icon: Key },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                activeTab === tab.id
                  ? "bg-violet-600/20 text-violet-300 border border-violet-500/40"
                  : "text-slate-400 hover:bg-slate-900"
              }`}
            >
              <Icon className="w-3.5 h-3.5" /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Pull Requests */}
      {activeTab === "prs" && (
        <div className="space-y-3">
          {prs.length === 0 ? (
            <p className="text-xs text-slate-500">No pull requests synced. Click Sync to fetch from VCS.</p>
          ) : (
            prs.map((pr: any) => (
              <div key={pr.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-violet-400">#{pr.number}</span>
                    <span className="font-bold text-slate-200">{pr.title}</span>
                    {pr.author && <span className="text-slate-500">by {pr.author}</span>}
                  </div>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] uppercase font-semibold">
                    {pr.state}
                  </span>
                </div>
                {pr.ai_review_summary ? (
                  <div className="p-3 rounded-lg bg-violet-950/20 border border-violet-500/30 text-[11px] text-violet-300 flex items-start gap-2">
                    <Sparkles className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
                    <span>{pr.ai_review_summary}</span>
                  </div>
                ) : (
                  <button
                    onClick={() => generateAIReview.mutate(pr.id)}
                    disabled={generateAIReview.isPending}
                    className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-violet-600/20 text-violet-300 border border-violet-500/30 text-xs hover:bg-violet-600/30 transition"
                  >
                    <Sparkles className="w-3.5 h-3.5" /> Run AI Code Review
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Issues */}
      {activeTab === "issues" && (
        <div className="space-y-3">
          {issues.length === 0 ? (
            <p className="text-xs text-slate-500">No issues synced yet.</p>
          ) : (
            issues.map((issue: any) => (
              <div key={issue.id} className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                <div className="flex items-center gap-3">
                  <CircleDot className={`w-4 h-4 ${issue.state === "open" ? "text-emerald-400" : "text-slate-500"}`} />
                  <div>
                    <span className="font-mono text-violet-400 mr-2">#{issue.number}</span>
                    <span className="font-bold text-slate-200">{issue.title}</span>
                    {issue.labels && (
                      <p className="text-[10px] text-slate-500 mt-0.5">{issue.labels}</p>
                    )}
                  </div>
                </div>
                {issue.html_url && (
                  <a href={issue.html_url} target="_blank" rel="noopener noreferrer" className="text-violet-400 hover:underline">
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Deployments */}
      {activeTab === "deployments" && (
        <div className="space-y-3">
          {deployments.length === 0 ? (
            <p className="text-xs text-slate-500">No deployments tracked yet.</p>
          ) : (
            deployments.map((dep: any) => {
              const StatusIcon = dep.status === "success" ? CheckCircle2 : AlertCircle;
              return (
                <div key={dep.id} className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                  <div className="flex items-center gap-3">
                    <StatusIcon className={`w-4 h-4 ${DEPLOYMENT_STATUS[dep.status] || "text-slate-400"}`} />
                    <div>
                      <span className="font-bold text-slate-200 capitalize">{dep.environment}</span>
                      <p className="text-[10px] font-mono text-slate-500 mt-0.5">
                        {dep.commit_hash ? `Commit: ${dep.commit_hash}` : "No commit hash"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-[10px] uppercase font-semibold ${DEPLOYMENT_STATUS[dep.status] || "text-slate-400"}`}>
                      {dep.status}
                    </span>
                    {dep.url && (
                      <a href={dep.url} target="_blank" rel="noopener noreferrer" className="text-violet-400 hover:underline flex items-center gap-1">
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Environment Variables */}
      {activeTab === "env" && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-xs font-semibold text-slate-400 uppercase">Encrypted Secrets</span>
            <button
              onClick={() => setShowEnvModal(true)}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-violet-600 text-white text-xs"
            >
              <Plus className="w-3 h-3" /> Add Secret
            </button>
          </div>

          {showEnvModal && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3 max-w-md">
              <input
                value={envKey}
                onChange={(e) => setEnvKey(e.target.value)}
                placeholder="KEY (e.g. DATABASE_URL)"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs"
              />
              <input
                value={envVal}
                onChange={(e) => setEnvVal(e.target.value)}
                type="password"
                placeholder="VALUE"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs"
              />
              <div className="flex justify-end gap-2">
                <button onClick={() => setShowEnvModal(false)} className="px-3 py-1 rounded bg-slate-800 text-slate-400 text-xs">Cancel</button>
                <button onClick={() => addEnvVar.mutate()} disabled={!envKey.trim()} className="px-3 py-1 rounded bg-violet-600 text-white text-xs disabled:opacity-50">Save</button>
              </div>
            </div>
          )}

          <div className="border border-slate-800 rounded-xl overflow-hidden text-xs">
            <table className="w-full">
              <thead className="bg-slate-900/60 border-b border-slate-800">
                <tr>
                  <th className="text-left px-4 py-2.5 text-slate-500">Key</th>
                  <th className="text-left px-4 py-2.5 text-slate-500">Value</th>
                  <th className="text-left px-4 py-2.5 text-slate-500">Environment</th>
                  <th className="w-10"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {envVars.length === 0 ? (
                  <tr><td colSpan={4} className="px-4 py-6 text-center text-slate-500">No secrets stored</td></tr>
                ) : (
                  envVars.map((ev: any) => (
                    <tr key={ev.id}>
                      <td className="px-4 py-2 font-mono text-slate-200 font-bold">{ev.key}</td>
                      <td className="px-4 py-2 font-mono text-slate-500">••••••••••••••••</td>
                      <td className="px-4 py-2 capitalize text-slate-400">{ev.environment}</td>
                      <td className="px-2 py-2">
                        <button onClick={() => deleteEnvVar.mutate(ev.id)} className="text-slate-600 hover:text-red-400">
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
