"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import Link from "next/link";
import { FolderKanban, FileText, Receipt, LifeBuoy, CheckCircle2, ArrowRight } from "lucide-react";

export default function ClientDashboardPage() {
  const mockCompanyId = "00000000-0000-0000-0000-000000000001";

  const { data: projects = [] } = useQuery({
    queryKey: ["portal-projects", mockCompanyId],
    queryFn: () => apiClient(`/api/v1/portal/company/${mockCompanyId}/projects`).then((r: any) => r.data || []),
  });

  const { data: proposals = [] } = useQuery({
    queryKey: ["portal-proposals", mockCompanyId],
    queryFn: () => apiClient(`/api/v1/portal/company/${mockCompanyId}/proposals`).then((r: any) => r.data || []),
  });

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-violet-900/40 via-indigo-900/30 to-slate-900 border border-violet-500/30 space-y-2">
        <h1 className="text-xl font-bold text-white">Client Portal Overview</h1>
        <p className="text-xs text-slate-300">Track active software projects, review proposals, download invoices, and request support.</p>
      </div>

      {/* Grid of Scoped Client Data */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Projects Progress Box */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FolderKanban className="w-4 h-4 text-violet-400" />
              <h2 className="text-sm font-bold text-white">Active Projects ({projects.length})</h2>
            </div>
          </div>

          <div className="space-y-2">
            {projects.length === 0 ? (
              <p className="text-xs text-slate-500 py-4 text-center">No active projects assigned yet.</p>
            ) : (
              projects.map((p: any) => (
                <div key={p.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-medium text-slate-200 block">{p.name}</span>
                    <span className="text-[10px] text-slate-500 capitalize">{p.status}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-semibold">Active</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Proposals & Contracts Box */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-white">Shared Proposals & SOWs</h2>
            </div>
            <Link href="/portal/documents" className="text-xs text-violet-400 hover:underline">View All</Link>
          </div>

          <div className="space-y-2">
            {proposals.length === 0 ? (
              <p className="text-xs text-slate-500 py-4 text-center">No documents shared yet.</p>
            ) : (
              proposals.map((doc: any) => (
                <div key={doc.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-medium text-slate-200 block">{doc.title}</span>
                    <span className="text-[10px] text-slate-500 uppercase">{doc.type.replace("_", " ")}</span>
                  </div>
                  <span className="text-slate-300 font-bold">{doc.total_value ? `${doc.currency || '$'}${Number(doc.total_value).toLocaleString()}` : "—"}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
