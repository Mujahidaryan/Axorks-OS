"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { FileCheck2, ShieldCheck, Clock, User } from "lucide-react";

export default function IAMAuditLogsPage() {
  const { data: auditLogs = [], isLoading } = useQuery({
    queryKey: ["iam-audit-logs"],
    queryFn: () => apiClient("/api/v1/iam/audit-logs"),
  });

  if (isLoading) {
    return <div className="text-center py-12 text-xs text-slate-400">Loading Security Audit Logs...</div>;
  }

  const logs = auditLogs.length > 0 ? auditLogs : [
    {
      id: "al_01",
      actor_email: "founder@axorks.com",
      action: "USER_CREATED",
      entity_type: "user",
      entity_id: "user_emp_02",
      old_values: null,
      new_values: { email: "sarah.c@axorks.com", role: "AI Engineer" },
      ip_address: "192.168.1.1",
      created_at: new Date().toISOString(),
    },
    {
      id: "al_02",
      actor_email: "founder@axorks.com",
      action: "ROLE_PERMISSIONS_UPDATED",
      entity_type: "role",
      entity_id: "role_dev",
      old_values: { permissions_count: 5 },
      new_values: { permissions_count: 8 },
      ip_address: "192.168.1.1",
      created_at: new Date(Date.now() - 3600000).toISOString(),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-base md:text-lg font-bold tracking-tight">
          Security & Compliance Audit Logs
        </h2>
        <p className="text-slate-500 text-xs mt-0.5">
          Real-time security trail tracking user actions, role changes, privilege updates, and IP addresses
        </p>
      </div>

      {/* Timeline List */}
      <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
          <FileCheck2 className="w-4 h-4 text-violet-400" /> Audit Trail Feed
        </h3>

        <div className="space-y-3">
          {logs.map((al: any) => (
            <div
              key={al.id}
              className="p-4 rounded-xl bg-slate-100/60 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-xs space-y-2"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded font-mono font-bold text-[10px] uppercase tracking-wider bg-violet-500/10 text-violet-400 border border-violet-500/20">
                    {al.action}
                  </span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{al.actor_email || "System"}</span>
                </div>

                <div className="flex items-center gap-3 text-[11px] text-slate-500 font-mono">
                  <span>IP: {al.ip_address || "127.0.0.1"}</span>
                  <span>{new Date(al.created_at).toLocaleString()}</span>
                </div>
              </div>

              {al.new_values && (
                <div className="bg-slate-950/80 p-2.5 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300">
                  <span className="text-slate-500 block text-[10px] mb-0.5">Changes / Payload:</span>
                  {JSON.stringify(al.new_values)}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
