"use client";

import { useEffect } from "react";
import { useUIStore } from "@/stores/ui-store";
import { Command } from "cmdk";
import { useRouter } from "next/navigation";
import { Target, Users, FolderKanban, Receipt, Settings } from "lucide-react";

export function CommandPalette() {
  const { commandPaletteOpen, setCommandPaletteOpen } = useUIStore();
  const router = useRouter();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [commandPaletteOpen, setCommandPaletteOpen]);

  if (!commandPaletteOpen) return null;

  const navigate = (path: string) => {
    setCommandPaletteOpen(false);
    router.push(path);
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg glass rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
        <Command className="w-full">
          <Command.Input
            placeholder="Type a command or search..."
            className="w-full px-4 py-3 bg-transparent border-b border-slate-800 text-sm focus:outline-none text-slate-100"
          />
          <Command.List className="p-2 max-h-64 overflow-y-auto text-xs">
            <Command.Empty className="py-4 text-center text-slate-500">
              No results found.
            </Command.Empty>

            <Command.Group heading="Navigation" className="text-slate-500 font-semibold px-2 py-1">
              <Command.Item
                onSelect={() => navigate("/leads")}
                className="flex items-center gap-2 p-2 rounded hover:bg-violet-600/20 cursor-pointer text-slate-200"
              >
                <Target className="w-4 h-4 text-violet-400" /> Go to Leads
              </Command.Item>
              <Command.Item
                onSelect={() => navigate("/crm")}
                className="flex items-center gap-2 p-2 rounded hover:bg-violet-600/20 cursor-pointer text-slate-200"
              >
                <Users className="w-4 h-4 text-violet-400" /> Go to CRM
              </Command.Item>
              <Command.Item
                onSelect={() => navigate("/projects")}
                className="flex items-center gap-2 p-2 rounded hover:bg-violet-600/20 cursor-pointer text-slate-200"
              >
                <FolderKanban className="w-4 h-4 text-violet-400" /> Go to Projects
              </Command.Item>
              <Command.Item
                onSelect={() => navigate("/finance")}
                className="flex items-center gap-2 p-2 rounded hover:bg-violet-600/20 cursor-pointer text-slate-200"
              >
                <Receipt className="w-4 h-4 text-violet-400" /> Go to Finance
              </Command.Item>
              <Command.Item
                onSelect={() => navigate("/settings")}
                className="flex items-center gap-2 p-2 rounded hover:bg-violet-600/20 cursor-pointer text-slate-200"
              >
                <Settings className="w-4 h-4 text-violet-400" /> Go to Settings
              </Command.Item>
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
