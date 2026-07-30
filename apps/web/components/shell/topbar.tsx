"use client";

import { useUIStore } from "@/stores/ui-store";
import { Search, Bell } from "lucide-react";
import { ThemeToggle } from "./theme-toggle";
import { Breadcrumbs } from "./breadcrumbs";

export function Topbar() {
  const { setCommandPaletteOpen, toggleNotifications } = useUIStore();

  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-950/70 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Breadcrumbs */}
      <Breadcrumbs />

      {/* Action icons & Search trigger */}
      <div className="flex items-center gap-3">
        {/* Cmd+K trigger */}
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition"
        >
          <Search className="w-3.5 h-3.5" />
          <span>Search or command...</span>
          <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-[10px] font-mono text-slate-500">
            ⌘K
          </kbd>
        </button>

        {/* Notifications Bell */}
        <button
          onClick={toggleNotifications}
          className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900 transition relative"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-violet-500" />
        </button>

        {/* Dark/Light mode toggle */}
        <ThemeToggle />
      </div>
    </header>
  );
}
