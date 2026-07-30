"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Plug, Plus, Check, X, Trash2, Power } from "lucide-react";

const PROVIDER_ICONS: Record<string, string> = {
  google: "🔵",
  microsoft: "🟦",
  github: "🐙",
  gitlab: "🦊",
  bitbucket: "🔵",
  slack: "💬",
  discord: "🎮",
  whatsapp: "📱",
  stripe: "💳",
  paypal: "💰",
  resend: "📧",
  openai: "🤖",
  anthropic: "🧠",
  google_ai: "✨",
  deepseek: "🔍",
  linkedin: "💼",
  facebook: "👍",
  instagram: "📸",
  youtube: "▶️",
  google_analytics: "📊",
  search_console: "🔎",
};

export default function IntegrationsPage() {
  const queryClient = useQueryClient();
  const [showConnect, setShowConnect] = useState<string | null>(null);
  const [instanceName, setInstanceName] = useState("");
  const [configJson, setConfigJson] = useState("{}");

  const { data: providers = [] } = useQuery({
    queryKey: ["integration-providers"],
    queryFn: () => apiClient("/api/v1/integrations/providers"),
  });

  const { data: instances = [] } = useQuery({
    queryKey: ["integration-instances"],
    queryFn: () => apiClient("/api/v1/integrations/instances"),
  });

  const createInstance = useMutation({
    mutationFn: ({ providerId, name, config }: { providerId: string; name: string; config: any }) =>
      apiClient("/api/v1/integrations/instances", {
        method: "POST",
        body: JSON.stringify({ provider_id: providerId, name, config }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["integration-instances"] });
      toast.success("Integration connected!");
      setShowConnect(null);
      setInstanceName("");
      setConfigJson("{}");
    },
    onError: (err: any) => toast.error(err.message || "Failed to connect"),
  });

  const toggleInstance = useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      apiClient(`/api/v1/integrations/instances/${id}/toggle?enabled=${enabled}`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["integration-instances"] });
      toast.success("Integration updated");
    },
  });

  const deleteInstance = useMutation({
    mutationFn: (id: string) => apiClient(`/api/v1/integrations/instances/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["integration-instances"] });
      toast.success("Integration disconnected");
    },
  });

  const connectedProviderIds = new Set(instances.map((i: any) => i.provider_id));

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">Integrations</h1>
        <p className="text-xs text-slate-500 mt-0.5">Connect external services via OAuth and API keys</p>
      </div>

      {/* Connected Integrations */}
      {instances.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Connected ({instances.length})</h2>
          <div className="space-y-2">
            {instances.map((inst: any) => {
              const provider = providers.find((p: any) => p.id === inst.provider_id);
              return (
                <div key={inst.id} className="flex items-center justify-between p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{PROVIDER_ICONS[provider?.name] || "🔌"}</span>
                    <div>
                      <span className="font-medium text-slate-800 dark:text-slate-200 text-xs block">{inst.name}</span>
                      <span className="text-[10px] text-slate-500 capitalize">{provider?.name} · {provider?.config_schema?.type}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${inst.enabled ? "bg-green-500/10 text-green-400" : "bg-slate-500/10 text-slate-400"}`}>
                      {inst.enabled ? "Active" : "Disabled"}
                    </span>
                    <button onClick={() => toggleInstance.mutate({ id: inst.id, enabled: !inst.enabled })} className="p-1.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-violet-500">
                      <Power className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => deleteInstance.mutate(inst.id)} className="p-1.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-red-500">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Available Providers */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Available ({providers.length})</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {providers.map((provider: any) => {
            const isConnected = connectedProviderIds.has(provider.id);
            return (
              <div key={provider.id} className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-violet-500/40 transition">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-2xl">{PROVIDER_ICONS[provider.name] || "🔌"}</span>
                  {isConnected ? (
                    <span className="flex items-center gap-1 text-[10px] text-green-500 font-medium">
                      <Check className="w-3 h-3" /> Connected
                    </span>
                  ) : (
                    <button
                      onClick={() => {
                        setShowConnect(provider.id);
                        setInstanceName(provider.name.charAt(0).toUpperCase() + provider.name.slice(1));
                        const fields = provider.config_schema?.fields || [];
                        const initialConfig: Record<string, string> = {};
                        fields.forEach((f: string) => (initialConfig[f] = ""));
                        setConfigJson(JSON.stringify(initialConfig, null, 2));
                      }}
                      className="flex items-center gap-1 text-[10px] text-violet-500 font-medium hover:text-violet-400"
                    >
                      <Plus className="w-3 h-3" /> Connect
                    </button>
                  )}
                </div>
                <span className="text-xs font-medium text-slate-800 dark:text-slate-200 capitalize block">{provider.name.replace(/_/g, " ")}</span>
                <span className="text-[10px] text-slate-500 capitalize">{provider.config_schema?.type}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Connect Modal */}
      {showConnect && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setShowConnect(null)}>
          <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 max-w-md w-full space-y-3" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Connect Integration</h2>
            <input
              value={instanceName}
              onChange={(e) => setInstanceName(e.target.value)}
              placeholder="Instance name"
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white"
            />
            <div>
              <label className="text-[10px] uppercase tracking-wide text-slate-500 font-medium block mb-1">Configuration (JSON)</label>
              <textarea
                value={configJson}
                onChange={(e) => setConfigJson(e.target.value)}
                rows={6}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs font-mono text-slate-900 dark:text-white"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowConnect(null)} className="px-4 py-1.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 text-xs">Cancel</button>
              <button
                onClick={() => {
                  try {
                    const config = JSON.parse(configJson);
                    createInstance.mutate({ providerId: showConnect, name: instanceName, config });
                  } catch {
                    toast.error("Invalid JSON configuration");
                  }
                }}
                disabled={!instanceName.trim()}
                className="px-4 py-1.5 rounded bg-violet-600 text-white text-xs disabled:opacity-50"
              >
                Connect
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}