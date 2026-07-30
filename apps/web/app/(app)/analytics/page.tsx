"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { AISuggestionPanel } from "@/components/ai/ai-suggestion-panel";
import { BarChart3, TrendingUp, DollarSign, FolderKanban, Users, Target, Receipt } from "lucide-react";

export default function AnalyticsPage() {
  const { data: companyOverview } = useQuery({
    queryKey: ["analytics-company"],
    queryFn: () => apiClient("/api/v1/analytics/overview/company"),
  });

  const { data: salesOverview } = useQuery({
    queryKey: ["analytics-sales"],
    queryFn: () => apiClient("/api/v1/analytics/overview/sales"),
  });

  const { data: financeOverview } = useQuery({
    queryKey: ["analytics-finance"],
    queryFn: () => apiClient("/api/v1/analytics/overview/finance"),
  });

  const { data: projectsOverview } = useQuery({
    queryKey: ["analytics-projects"],
    queryFn: () => apiClient("/api/v1/analytics/overview/projects"),
  });

  const { data: dashboards = [] } = useQuery({
    queryKey: ["analytics-dashboards"],
    queryFn: () => apiClient("/api/v1/analytics/dashboards"),
  });

  const formatCurrency = (val: number) => {
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`;
    if (val >= 1000) return `$${(val / 1000).toFixed(1)}K`;
    return `$${val.toFixed(0)}`;
  };

  const salesStages = salesOverview?.leads_by_stage ? Object.entries(salesOverview.leads_by_stage) : [];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">Analytics</h1>
        <p className="text-xs text-slate-500 mt-0.5">Dashboards for company, sales, finance, projects & more</p>
      </div>

      {/* Company Overview KPIs */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Company Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <KpiCard icon={Target} label="Leads" value={companyOverview?.leads ?? 0} color="text-violet-500" />
          <KpiCard icon={Users} label="Companies" value={companyOverview?.companies ?? 0} color="text-blue-500" />
          <KpiCard icon={FolderKanban} label="Projects" value={companyOverview?.projects ?? 0} color="text-green-500" />
          <KpiCard icon={Receipt} label="Invoices" value={companyOverview?.invoices ?? 0} color="text-amber-500" />
        </div>
      </div>

      {/* Sales Pipeline */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-2">
          <TrendingUp className="w-4 h-4" /> Sales Pipeline
        </h2>
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          {salesStages.length > 0 ? (
            <div className="space-y-2">
              {salesStages.map(([stage, count]: [string, any]) => {
                const maxCount = Math.max(...salesStages.map(([, c]: [string, any]) => c), 1);
                const width = (count / maxCount) * 100;
                return (
                  <div key={stage} className="flex items-center gap-3">
                    <span className="text-[10px] text-slate-500 w-24 capitalize">{stage}</span>
                    <div className="flex-1 h-6 bg-slate-100 dark:bg-slate-800 rounded-lg overflow-hidden">
                      <div className="h-full bg-violet-500/60 rounded-lg flex items-center justify-end px-2" style={{ width: `${width}%` }}>
                        <span className="text-[10px] font-bold text-white">{count}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
              <div className="pt-3 border-t border-slate-200 dark:border-slate-800 mt-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-slate-500">Won Deals Value</span>
                  <span className="text-lg font-bold text-green-500">{formatCurrency(salesOverview?.won_deals_value ?? 0)}</span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500 text-center py-4">No sales data yet.</p>
          )}
        </div>
      </div>

      {/* Finance Overview */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-2">
          <DollarSign className="w-4 h-4" /> Finance Summary
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <KpiCard icon={DollarSign} label="Revenue" value={formatCurrency(financeOverview?.total_revenue ?? 0)} color="text-green-500" />
          <KpiCard icon={Receipt} label="Outstanding" value={formatCurrency(financeOverview?.total_outstanding ?? 0)} color="text-amber-500" />
          <KpiCard icon={TrendingUp} label="Expenses" value={formatCurrency(financeOverview?.total_expenses ?? 0)} color="text-red-500" />
          <KpiCard icon={BarChart3} label="Net Profit" value={formatCurrency(financeOverview?.net_profit ?? 0)} color="text-violet-500" />
        </div>
      </div>

      {/* Projects Overview */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-2">
          <FolderKanban className="w-4 h-4" /> Projects
        </h2>
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          {projectsOverview?.projects_by_status ? (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {Object.entries(projectsOverview.projects_by_status).map(([status, count]: [string, any]) => (
                <div key={status} className="text-center">
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">{count}</p>
                  <p className="text-[10px] uppercase tracking-wide text-slate-500 capitalize">{status.replace("_", " ")}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 text-center py-4">No project data yet.</p>
          )}
          {projectsOverview?.total_tasks !== undefined && (
            <div className="pt-3 border-t border-slate-200 dark:border-slate-800 mt-3 text-center">
              <span className="text-xs text-slate-500">Total Tasks: </span>
              <span className="text-sm font-bold text-slate-700 dark:text-slate-300">{projectsOverview.total_tasks}</span>
            </div>
          )}
        </div>
      </div>

      {/* AI Insights */}
      <AISuggestionPanel context="dashboard" title="AI Dashboard Insights" />

      {/* Custom Dashboards */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Custom Dashboards</h2>
        <div className="space-y-2">
          {dashboards.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">
              No custom dashboards configured. Create one via the API.
            </div>
          ) : (
            dashboards.map((dash: any) => (
              <div key={dash.id} className="p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                <span className="font-medium text-slate-800 dark:text-slate-200 text-xs">{dash.title}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function KpiCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: any; color: string }) {
  return (
    <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
      <Icon className={`w-4 h-4 ${color} mb-2`} />
      <p className="text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
      <p className="text-[10px] uppercase tracking-wide text-slate-500">{label}</p>
    </div>
  );
}