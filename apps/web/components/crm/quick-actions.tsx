"use client";

import { useState } from "react";
import { MessageSquare, Phone, Mail, Upload, Plus } from "lucide-react";

interface QuickActionsProps {
  onAddNote: () => void;
  onLogCall: () => void;
}

export function QuickActions({ onAddNote, onLogCall }: QuickActionsProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-8 right-8 z-40 flex flex-col items-end gap-2">
      {open && (
        <div className="space-y-2 mb-2">
          <button onClick={() => { onAddNote(); setOpen(false); }} className="flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/90 text-white text-xs font-medium shadow-lg hover:bg-amber-500 transition">
            <MessageSquare className="w-3.5 h-3.5" /> Add Note
          </button>
          <button onClick={() => { onLogCall(); setOpen(false); }} className="flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/90 text-white text-xs font-medium shadow-lg hover:bg-cyan-500 transition">
            <Phone className="w-3.5 h-3.5" /> Log Call
          </button>
        </div>
      )}

      <button
        onClick={() => setOpen(!open)}
        className="w-12 h-12 rounded-full bg-violet-600 hover:bg-violet-500 text-white shadow-xl shadow-violet-600/30 flex items-center justify-center transition-transform"
        style={{ transform: open ? "rotate(45deg)" : "rotate(0)" }}
      >
        <Plus className="w-5 h-5" />
      </button>
    </div>
  );
}
