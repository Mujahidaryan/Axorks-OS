"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import Link from "next/link";
import { DollarSign, TrendingUp, TrendingDown, Receipt, ArrowUpRight, AlertTriangle } from "lucide-react";

function StatCard({ label, value, icon: Icon, color, sub }: { label: string; value: string; icon: any; color: string; sub?: string }) {
  return (
    <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">{label}</span>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <p className="text-2xl font-bold text-white tracking-tight">{value}</p>
      {sub && <p className="text-[11px] text-slate-500">{sub}</p>}
    </div>
  );
}

export default function FinanceDashboardPage() {
  const { data: summary } = useQuery({
    queryKey: ["finance-dashboard"],
    queryFn: () => apiClient("/api/v1/finance/dashboard").then((r: any) => r.data),
  });

  const { data: forecast } = useQuery({
    queryKey: ["finance-forecast"],
    queryFn: () => apiClient("/api/v1/finance/forecast").then((r: any) => r.data),
  });

  const fmt = (n: number) => `$${(n || 0).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Financial Dashboard</h1>
          <p className="text-xs text-slate-500 mt-0.5">Revenue, expenses, cash flow, and forecasts</p>
        </div>
        <div className="flex gap-2">
          <Link href="/finance/invoices" className="px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition flex items-center gap-1.5">
            <Receipt className="w-3.5 h-3.5" /> Invoices
          </Link>
          <Link href="/finance/expenses" className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition">
            Expenses
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Revenue"
          value={fmt(summary?.total_revenue || 0)}
          icon={TrendingUp}
          color="bg-emerald-500/10 text-emerald-400"
          sub="All-time collected payments"
        />
        <StatCard
          label="Total Expenses"
          value={fmt(summary?.total_expenses || 0)}
          icon={TrendingDown}
          color="bg-red-500/10 text-red-400"
          sub="Operational + project costs"
        />
        <StatCard
          label="Net Profit"
          value={fmt(summary?.net_profit || 0)}
          icon={DollarSign}
          color="bg-violet-500/10 text-violet-400"
          sub="Revenue minus expenses"
        />
        <StatCard
          label="Outstanding Invoices"
          value={fmt(summary?.total_outstanding_invoices || 0)}
          icon={AlertTriangle}
          color="bg-amber-500/10 text-amber-400"
          sub="Unpaid invoice totals"
        />
      </div>

      {/* Cash Flow Forecast */}
      {forecast && (
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <ArrowUpRight className="w-4 h-4 text-cyan-400" /> 30-Day Cash Flow Forecast
            </h2>
            <span className="px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-[10px] font-semibold">
              {Math.round((forecast.confidence_score || 0) * 100)}% Confidence
            </span>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800/60 text-center">
              <p className="text-[10px] uppercase text-slate-500 font-semibold mb-1">Projected Revenue</p>
              <p className="text-lg font-bold text-emerald-400">{fmt(forecast["30_day_forecast"]?.projected_revenue)}</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800/60 text-center">
              <p className="text-[10px] uppercase text-slate-500 font-semibold mb-1">Projected Expenses</p>
              <p className="text-lg font-bold text-red-400">{fmt(forecast["30_day_forecast"]?.projected_expenses)}</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800/60 text-center">
              <p className="text-[10px] uppercase text-slate-500 font-semibold mb-1">Projected Cash Flow</p>
              <p className="text-lg font-bold text-violet-400">{fmt(forecast["30_day_forecast"]?.projected_cash_flow)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Revenue Chart Placeholder */}
      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
        <h2 className="text-sm font-bold text-white">Revenue by Month</h2>
        <div className="flex items-end gap-2 h-40">
          {["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"].map((m, i) => {
            const h = [35, 50, 45, 65, 72, 80, 90][i];
            return (
              <div key={m} className="flex-1 flex flex-col items-center gap-1">
                <div
                  className="w-full rounded-t-md bg-gradient-to-t from-violet-600 to-violet-400 transition-all"
                  style={{ height: `${h}%` }}
                />
                <span className="text-[10px] text-slate-500">{m}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
