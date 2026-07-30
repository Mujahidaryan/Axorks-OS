"use client";

import { useUIStore } from "@/stores/ui-store";
import { CheckCheck } from "lucide-react";

export function NotificationsPanel() {
  const { notificationsPanelOpen } = useUIStore();

  if (!notificationsPanelOpen) return null;

  return (
    <div className="absolute right-6 top-16 w-80 glass rounded-xl border border-slate-200 dark:border-slate-800 shadow-2xl z-50 p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Notifications
        </h3>
        <button className="text-[10px] text-violet-500 hover:underline flex items-center gap-1">
          <CheckCheck className="w-3 h-3" /> Mark all read
        </button>
      </div>

      <div className="text-center py-6 text-xs text-slate-400">
        No unread notifications right now
      </div>
    </div>
  );
}
