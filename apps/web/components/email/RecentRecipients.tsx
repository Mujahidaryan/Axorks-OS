"use client";

import { UserCheck, Plus } from "lucide-react";

interface RecentRecipientsProps {
  onSelect: (email: string) => void;
  selectedEmails: string[];
}

const RECENT_CONTACTS = [
  { name: "Alex Tech", email: "alex.tech@acmecorp.com", company: "Acme Corp" },
  { name: "Sarah Connor", email: "contact@innovate.io", company: "Innovate Tech" },
  { name: "David Miller", email: "finance@globaltech.org", company: "GlobalTech" },
  { name: "Jessica Alba", email: "jessica@apexsolutions.com", company: "Apex Solutions" },
];

export function RecentRecipients({ onSelect, selectedEmails }: RecentRecipientsProps) {
  return (
    <div className="space-y-1.5">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
        <UserCheck className="w-3 h-3 text-violet-500" /> Recent CRM Contacts
      </div>
      <div className="flex flex-wrap gap-1.5">
        {RECENT_CONTACTS.map((c) => {
          const isSelected = selectedEmails.includes(c.email);
          return (
            <button
              key={c.email}
              type="button"
              disabled={isSelected}
              onClick={() => onSelect(c.email)}
              className={`inline-flex items-center gap-1 text-[11px] px-2.5 py-1 rounded-md border transition ${
                isSelected
                  ? "bg-slate-100 dark:bg-slate-800/50 text-slate-400 border-slate-200 dark:border-slate-800 cursor-not-allowed"
                  : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-800 hover:border-violet-500 dark:hover:border-violet-500 hover:text-violet-600 dark:hover:text-violet-400"
              }`}
            >
              <Plus className="w-3 h-3" />
              <span className="font-semibold">{c.name}</span>
              <span className="text-slate-400">({c.company})</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
