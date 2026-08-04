"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import Link from "next/link";
import {
  Users,
  UserCheck,
  UserX,
  Lock,
  Clock,
  Video,
  ShieldAlert,
  ArrowRight,
  Sparkles,
  Plus,
} from "lucide-react";

export default function IAMDashboardPage() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["iam-dashboard"],
    queryFn: () => apiClient("/api/v1/iam/dashboard"),
  });

  if (isLoading) {
    return <div className="text-center py-12 text-xs text-slate-400">Loading Founder Overview...</div>;
  }

  const d = dashboard || {
    total_employees: 14,
    online_employees: 9,
    offline_employees: 3,
    locked_accounts: 0,
    suspended_accounts: 1,
    pending_invitations: 1,
    todays_logins: 11,
    failed_attempts: 0,
    recent_audit_logs: [],
    latest_joined: [],
    recent_recordings: [],
  };

  return (
    <div className="space-y-6">
      {/* KPI Stats Grid — Mobile First Responsive Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="glass p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Total</span>
            <Users className="w-4 h-4 text-violet-400" />
          </div>
          <div className="text-xl md:text-2xl font-bold">{d.total_employees}</div>
          <span className="text-[10px] text-slate-500">Employees</span>
        </div>

        <div className="glass p-4 rounded-xl border border-emerald-500/20 dark:border-emerald-500/20 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-500">Active</span>
            <UserCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl md:text-2xl font-bold text-emerald-400">{d.online_employees}</div>
          <span className="text-[10px] text-slate-500">Online now</span>
        </div>

        <div className="glass p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Offline</span>
            <UserX className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-xl md:text-2xl font-bold text-slate-400">{d.offline_employees}</div>
          <span className="text-[10px] text-slate-500">Inactive</span>
        </div>

        <div className="glass p-4 rounded-xl border border-amber-500/20 dark:border-amber-500/20 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-amber-500">Suspended</span>
            <Lock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xl md:text-2xl font-bold text-amber-400">{d.suspended_accounts}</div>
          <span className="text-[10px] text-slate-500">Accounts</span>
        </div>

        <div className="glass p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Pending</span>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-xl md:text-2xl font-bold text-cyan-400">{d.pending_invitations}</div>
          <span className="text-[10px] text-slate-500">Invitations</span>
        </div>

        <div className="glass p-4 rounded-xl border border-rose-500/20 dark:border-rose-500/20 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-rose-500">Failed Logins</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-xl md:text-2xl font-bold text-rose-400">{d.failed_attempts}</div>
          <span className="text-[10px] text-slate-500">Last 24 hours</span>
        </div>
      </div>

      {/* Founder Quick Control Bar */}
      <div className="glass p-4 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-violet-500" />
          <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
            Founder Quick Management Actions
          </span>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Link
            href="/iam/users?action=new"
            className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition shadow-md shadow-violet-600/20"
          >
            <Plus className="w-3.5 h-3.5" /> Add Employee
          </Link>
          <Link
            href="/iam/recordings"
            className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-medium hover:bg-slate-100 dark:hover:bg-slate-900 transition"
          >
            <Video className="w-3.5 h-3.5 text-violet-400" /> Screen & Call Recording
          </Link>
        </div>
      </div>

      {/* Main Responsive Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Employees */}
        <div className="glass p-5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-violet-500" /> Recently Joined Employees
            </h2>
            <Link href="/iam/users" className="text-xs text-violet-600 dark:text-violet-400 hover:underline flex items-center gap-1">
              View All <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-2">
            {d.latest_joined.length === 0 ? (
              <div className="text-xs text-slate-400 py-4 text-center">No recent joinings.</div>
            ) : (
              d.latest_joined.map((u: any) => (
                <div
                  key={u.id}
                  className="p-3 rounded-xl bg-slate-100/60 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/60 flex items-center justify-between gap-3 text-xs"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 rounded-full bg-violet-600/20 text-violet-400 font-bold flex items-center justify-center text-xs flex-shrink-0">
                      {u.first_name[0]}
                    </div>
                    <div className="min-w-0">
                      <div className="font-semibold text-slate-900 dark:text-slate-100 truncate">
                        {u.first_name} {u.last_name}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate">{u.email}</div>
                    </div>
                  </div>

                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold capitalize bg-violet-500/10 text-violet-500 border border-violet-500/20">
                    {u.role}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Founder Screen & Call Recordings Overview */}
        <div className="glass p-5 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
              <Video className="w-4 h-4 text-cyan-400" /> Screen & Call Recordings
            </h2>
            <Link href="/iam/recordings" className="text-xs text-cyan-500 dark:text-cyan-400 hover:underline flex items-center gap-1">
              Open Studio <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-2">
            {d.recent_recordings.length === 0 ? (
              <div className="text-xs text-slate-400 py-4 text-center">No recordings yet. Open Studio to start recording screen or call audio.</div>
            ) : (
              d.recent_recordings.map((r: any) => (
                <div
                  key={r.id}
                  className="p-3 rounded-xl bg-slate-100/60 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/60 flex items-center justify-between gap-3 text-xs"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center flex-shrink-0">
                      <Video className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="font-semibold text-slate-900 dark:text-slate-100 truncate">
                        {r.title}
                      </div>
                      <div className="text-[11px] text-slate-500 capitalize">{r.type} recording • {r.duration}s</div>
                    </div>
                  </div>

                  <span className="text-[10px] text-slate-400 font-mono">
                    {new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
