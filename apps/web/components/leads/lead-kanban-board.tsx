"use client";

import Link from "next/link";
import { AIScoreBadge } from "./ai-score-badge";

const COLUMNS = [
  { id: "new", label: "New" },
  { id: "contacted", label: "Contacted" },
  { id: "qualified", label: "Qualified" },
  { id: "proposal", label: "Proposal" },
  { id: "negotiation", label: "Negotiation" },
  { id: "won", label: "Won" },
];

interface LeadKanbanBoardProps {
  leads: any[];
}

export function LeadKanbanBoard({ leads }: LeadKanbanBoardProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-6 gap-3 overflow-x-auto pb-4">
      {COLUMNS.map((col) => {
        const columnLeads = leads.filter((l) => l.status === col.id);

        return (
          <div key={col.id} className="glass rounded-xl p-3 border border-slate-200 dark:border-slate-800 flex flex-col min-h-[400px]">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2 mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                {col.label}
              </span>
              <span className="px-1.5 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-[10px] text-slate-400 font-mono">
                {columnLeads.length}
              </span>
            </div>

            <div className="space-y-2 flex-1">
              {columnLeads.map((lead) => (
                <Link
                  key={lead.id}
                  href={`/leads/${lead.id}`}
                  className="block p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-violet-500 transition space-y-2 shadow-sm"
                >
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-semibold text-slate-900 dark:text-slate-100 line-clamp-1">
                      {lead.business_name || "Untitled Lead"}
                    </span>
                    <AIScoreBadge score={lead.score} showIcon={false} />
                  </div>
                  {lead.decision_maker_name && (
                    <div className="text-[10px] text-slate-400">
                      {lead.decision_maker_name}
                    </div>
                  )}
                  <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-slate-100 dark:border-slate-800/50">
                    <span className="capitalize">{lead.source}</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
