"use client";

import Link from "next/link";
import { AIScoreBadge } from "./ai-score-badge";
import { ExternalLink, Mail, Phone } from "lucide-react";

interface LeadTableViewProps {
  leads: any[];
}

export function LeadTableView({ leads }: LeadTableViewProps) {
  if (leads.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500 text-xs glass rounded-xl border border-slate-800">
        No leads match your criteria. Create one or adjust your filters.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto glass rounded-xl border border-slate-200 dark:border-slate-800">
      <table className="w-full text-left text-xs">
        <thead className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 text-slate-500 font-semibold uppercase tracking-wider">
          <tr>
            <th className="p-3">Business</th>
            <th className="p-3">Decision Maker</th>
            <th className="p-3">Status</th>
            <th className="p-3">Score</th>
            <th className="p-3">Source</th>
            <th className="p-3">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
          {leads.map((lead) => (
            <tr key={lead.id} className="hover:bg-slate-100/50 dark:hover:bg-slate-900/50 transition">
              <td className="p-3">
                <Link href={`/leads/${lead.id}`} className="font-semibold text-slate-900 dark:text-slate-100 hover:text-violet-500">
                  {lead.business_name || "Untitled Business"}
                </Link>
                {lead.website && (
                  <div className="text-[10px] text-slate-400 flex items-center gap-1 mt-0.5">
                    <ExternalLink className="w-2.5 h-2.5" />
                    <a href={lead.website.startsWith("http") ? lead.website : `https://${lead.website}`} target="_blank" rel="noreferrer" className="hover:underline">
                      {lead.website}
                    </a>
                  </div>
                )}
              </td>
              <td className="p-3">
                <div className="font-medium text-slate-800 dark:text-slate-200">
                  {lead.decision_maker_name || "—"}
                </div>
                <div className="text-[10px] text-slate-400">
                  {lead.decision_maker_title || lead.email || ""}
                </div>
              </td>
              <td className="p-3">
                <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-violet-500/10 text-violet-600 dark:text-violet-400 border border-violet-500/20">
                  {lead.status}
                </span>
              </td>
              <td className="p-3">
                <AIScoreBadge score={lead.score} />
              </td>
              <td className="p-3 text-slate-400 capitalize">
                {lead.source}
              </td>
              <td className="p-3">
                <Link href={`/leads/${lead.id}`} className="px-2 py-1 rounded bg-slate-200 dark:bg-slate-800 hover:bg-violet-600 hover:text-white transition text-[10px]">
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
