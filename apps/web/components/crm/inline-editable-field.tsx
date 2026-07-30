"use client";

import { useState } from "react";
import { Check, X, Pencil } from "lucide-react";

interface InlineEditableFieldProps {
  label: string;
  value: string | null | undefined;
  onSave: (value: string) => void;
}

export function InlineEditableField({ label, value, onSave }: InlineEditableFieldProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value || "");

  const handleSave = () => {
    onSave(draft);
    setEditing(false);
  };

  const handleCancel = () => {
    setDraft(value || "");
    setEditing(false);
  };

  if (editing) {
    return (
      <div className="space-y-1">
        <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">{label}</span>
        <div className="flex items-center gap-1.5">
          <input
            type="text"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            autoFocus
            className="flex-1 px-2 py-1 bg-slate-900 border border-violet-500 rounded text-xs focus:outline-none"
            onKeyDown={(e) => e.key === "Enter" && handleSave()}
          />
          <button onClick={handleSave} className="p-1 rounded bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/40">
            <Check className="w-3 h-3" />
          </button>
          <button onClick={handleCancel} className="p-1 rounded bg-slate-800 text-slate-400 hover:bg-slate-700">
            <X className="w-3 h-3" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="group space-y-1 cursor-pointer" onClick={() => setEditing(true)}>
      <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">{label}</span>
      <div className="flex items-center gap-1.5">
        <span className="text-xs font-medium text-slate-200">{value || "—"}</span>
        <Pencil className="w-2.5 h-2.5 text-slate-600 opacity-0 group-hover:opacity-100 transition" />
      </div>
    </div>
  );
}
