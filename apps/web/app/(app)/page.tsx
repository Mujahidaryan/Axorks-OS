"use client";

import { Target, Users, FolderKanban, Receipt, ArrowUpRight, Sparkles } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 text-white relative overflow-hidden shadow-xl">
        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" /> Axorks OS — Phase 1: Foundation Active
          </div>
          <h1 className="text-2xl font-bold">Welcome to Axorks OS</h1>
          <p className="text-violet-100 text-sm max-w-xl">
            The AI-powered operating system for software houses, engineering consultancies, and digital agencies.
          </p>
        </div>
      </div>

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-500">
            <span className="text-xs font-medium">Leads Captured</span>
            <Target className="w-4 h-4 text-violet-500" />
          </div>
          <div className="text-2xl font-bold">0</div>
          <div className="text-[10px] text-slate-400">Phase 2: Lead Intelligence</div>
        </div>

        <div className="glass p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-500">
            <span className="text-xs font-medium">Active CRM Deals</span>
            <Users className="w-4 h-4 text-cyan-500" />
          </div>
          <div className="text-2xl font-bold">0</div>
          <div className="text-[10px] text-slate-400">Phase 3: One-Page CRM</div>
        </div>

        <div className="glass p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-500">
            <span className="text-xs font-medium">Active Projects</span>
            <FolderKanban className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold">0</div>
          <div className="text-[10px] text-slate-400">Phase 6: Project Management</div>
        </div>

        <div className="glass p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-slate-500">
            <span className="text-xs font-medium">Monthly Revenue</span>
            <Receipt className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold">$0</div>
          <div className="text-[10px] text-slate-400">Phase 9: Finance</div>
        </div>
      </div>
    </div>
  );
}
