"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient, apiClientPaginated } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import {
  Code2, Plus, Github, ExternalLink, GitBranch, RefreshCw, Link2,
} from "lucide-react";

export default function DevHubPage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [showConnectRepo, setShowConnectRepo] = useState(false);
  const [repoName, setRepoName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [provider, setProvider] = useState("github");
  const [selectedProjectId, setSelectedProjectId] = useState("");

  const { data: repos = [], isLoading } = useQuery({
    queryKey: ["dev-repos"],
    queryFn: () => apiClient<any[]>("/api/v1/dev/repos"),
  });

  const { data: integrations = [] } = useQuery({
    queryKey: ["vcs-integrations"],
    queryFn: () => apiClient<any[]>("/api/v1/dev/integrations/vcs"),
  });

  const { data: projectsData } = useQuery({
    queryKey: ["projects-select"],
    queryFn: () => apiClientPaginated<any>("/api/v1/projects?per_page=100"),
  });
  const projects = projectsData?.data || [];

  const connectRepo = useMutation({
    mutationFn: () =>
      apiClient<any>("/api/v1/dev/repos", {
        method: "POST",
        body: JSON.stringify({
          provider,
          external_repo_id: repoName.toLowerCase().replace(/\s+/g, "-"),
          name: repoName,
          full_name: `axorks/${repoName.toLowerCase().replace(/\s+/g, "-")}`,
          html_url: repoUrl || `https://github.com/axorks/${repoName}`,
          default_branch: "main",
          is_private: true,
          project_id: selectedProjectId || null,
        }),
      }),
    onSuccess: (repo) => {
      queryClient.invalidateQueries({ queryKey: ["dev-repos"] });
      toast.success("Repository linked!");
      setShowConnectRepo(false);
      setRepoName("");
      setRepoUrl("");
      setSelectedProjectId("");
      router.push(`/dev/repos/${repo.id}`);
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const connectVCS = useMutation({
    mutationFn: async (vcsProvider: string) => {
      if (vcsProvider === "github") {
        try {
          const oauth = await apiClient<{ url: string; state: string }>(
            "/api/v1/dev/oauth/github/authorize"
          );
          if (oauth?.url) {
            window.location.href = oauth.url;
            return null;
          }
        } catch {
          // Fall through to manual/mock connect when OAuth not configured
        }
      }
      return apiClient("/api/v1/dev/integrations/vcs", {
        method: "POST",
        body: JSON.stringify({
          provider: vcsProvider,
          access_token: `mock_${vcsProvider}_token`,
          account_username: "axorks-org",
        }),
      });
    },
    onSuccess: (res) => {
      if (res) {
        queryClient.invalidateQueries({ queryKey: ["vcs-integrations"] });
        toast.success("VCS integration connected!");
      }
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Development Hub</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            VCS integrations, pull requests, issues, deployments &amp; env secrets
          </p>
        </div>
        <button
          onClick={() => setShowConnectRepo(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition"
        >
          <Plus className="w-3.5 h-3.5" /> Connect Repository
        </button>
      </div>

      {/* VCS Connections */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-slate-800 flex items-center justify-center text-white">
            <Github className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-white">VCS Account Connections</h2>
            <p className="text-[11px] text-slate-400">
              Connect GitHub, GitLab, or Bitbucket for automatic PR, issue &amp; deployment sync.
            </p>
          </div>
        </div>
        <div className="flex gap-2 flex-wrap">
          {["github", "gitlab", "bitbucket"].map((prov) => {
            const connected = integrations.some((i: any) => i.provider === prov);
            return (
              <button
                key={prov}
                onClick={() => !connected && connectVCS.mutate(prov)}
                disabled={connectVCS.isPending}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition ${
                  connected
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                    : "bg-slate-800 hover:bg-slate-700 text-slate-300"
                }`}
              >
                {connected ? `✓ ${prov}` : `Connect ${prov}`}
              </button>
            );
          })}
        </div>
      </div>

      {/* Connect Repo Form */}
      {showConnectRepo && (
        <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 max-w-lg space-y-3">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2">
            <Link2 className="w-4 h-4 text-violet-400" /> Link Repository
          </h2>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
          >
            <option value="github">GitHub</option>
            <option value="gitlab">GitLab</option>
            <option value="bitbucket">Bitbucket</option>
          </select>
          <input
            value={repoName}
            onChange={(e) => setRepoName(e.target.value)}
            placeholder="Repository name (e.g. axorks-core-api)"
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs"
          />
          <input
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="Repository URL (optional)"
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs"
          />
          <select
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
          >
            <option value="">Link to project (optional)</option>
            {projects.map((p: any) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setShowConnectRepo(false)}
              className="px-4 py-1.5 rounded bg-slate-800 text-slate-400 text-xs"
            >
              Cancel
            </button>
            <button
              onClick={() => connectRepo.mutate()}
              disabled={!repoName.trim() || connectRepo.isPending}
              className="px-4 py-1.5 rounded bg-violet-600 text-white text-xs disabled:opacity-50"
            >
              Link Repository
            </button>
          </div>
        </div>
      )}

      {/* Repositories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading ? (
          <div className="col-span-full py-8 text-center text-xs text-slate-500">Loading repositories...</div>
        ) : repos.length === 0 ? (
          <div className="col-span-full py-8 text-center text-xs text-slate-500">
            No repositories linked yet. Connect a VCS account, then link a repo.
          </div>
        ) : (
          repos.map((repo: any) => (
            <div
              key={repo.id}
              onClick={() => router.push(`/dev/repos/${repo.id}`)}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-violet-500/40 transition cursor-pointer space-y-3 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Code2 className="w-4 h-4 text-violet-400" />
                  <span className="font-bold text-slate-200 text-xs group-hover:text-violet-300 transition">
                    {repo.name}
                  </span>
                </div>
                <span className="text-[10px] uppercase font-semibold text-slate-500 bg-slate-800 px-2 py-0.5 rounded">
                  {repo.provider}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono truncate">{repo.full_name}</p>
              <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-[10px] text-slate-500">
                <span className="flex items-center gap-1">
                  <GitBranch className="w-3 h-3" />
                  {repo.default_branch}
                </span>
                {repo.project_id && (
                  <span className="text-violet-400">Linked to project</span>
                )}
                <ExternalLink className="w-3 h-3 text-slate-600" />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
