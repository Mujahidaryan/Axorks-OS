"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Building2, Plus, Users, CalendarDays, Clock, Star, ChevronRight, Check, X } from "lucide-react";

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-500/10 text-green-400",
  on_leave: "bg-amber-500/10 text-amber-400",
  terminated: "bg-red-500/10 text-red-400",
  pending: "bg-amber-500/10 text-amber-400",
  approved: "bg-green-500/10 text-green-400",
  rejected: "bg-red-500/10 text-red-400",
};

export default function HRPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [position, setPosition] = useState("");
  const [department, setDepartment] = useState("");
  const [activeTab, setActiveTab] = useState<"employees" | "leaves" | "reviews">("employees");

  const { data: overview } = useQuery({
    queryKey: ["hr-overview"],
    queryFn: () => apiClient("/api/v1/hr/overview"),
  });

  const { data: employees = [] } = useQuery({
    queryKey: ["hr-employees"],
    queryFn: () => apiClient("/api/v1/hr/employees"),
  });

  const { data: leaves = [] } = useQuery({
    queryKey: ["hr-leaves"],
    queryFn: () => apiClient("/api/v1/hr/leaves"),
  });

  const { data: reviews = [] } = useQuery({
    queryKey: ["hr-reviews"],
    queryFn: () => apiClient("/api/v1/hr/reviews"),
  });

  const createEmployee = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/hr/employees", {
        method: "POST",
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          email,
          position: position || undefined,
          department: department || undefined,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["hr-employees"] });
      queryClient.invalidateQueries({ queryKey: ["hr-overview"] });
      toast.success("Employee added!");
      setShowCreate(false);
      setFirstName("");
      setLastName("");
      setEmail("");
      setPosition("");
      setDepartment("");
    },
  });

  const approveLeave = useMutation({
    mutationFn: (leaveId: string) =>
      apiClient(`/api/v1/hr/leaves/${leaveId}/approve`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["hr-leaves"] });
      toast.success("Leave approved");
    },
  });

  const rejectLeave = useMutation({
    mutationFn: (leaveId: string) =>
      apiClient(`/api/v1/hr/leaves/${leaveId}/reject`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["hr-leaves"] });
      toast.success("Leave rejected");
    },
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">HR</h1>
          <p className="text-xs text-slate-500 mt-0.5">Employees, attendance, leaves, payroll & performance</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition"
        >
          <Plus className="w-3.5 h-3.5" /> Add Employee
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <Users className="w-4 h-4 text-violet-500 mb-2" />
          <p className="text-2xl font-bold text-slate-900 dark:text-white">{overview?.total_employees ?? 0}</p>
          <p className="text-[10px] uppercase tracking-wide text-slate-500">Employees</p>
        </div>
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <CalendarDays className="w-4 h-4 text-amber-500 mb-2" />
          <p className="text-2xl font-bold text-slate-900 dark:text-white">{overview?.pending_leaves ?? 0}</p>
          <p className="text-[10px] uppercase tracking-wide text-slate-500">Pending Leaves</p>
        </div>
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <Clock className="w-4 h-4 text-blue-500 mb-2" />
          <p className="text-2xl font-bold text-slate-900 dark:text-white">{overview?.on_leave ?? 0}</p>
          <p className="text-[10px] uppercase tracking-wide text-slate-500">On Leave</p>
        </div>
      </div>

      {/* Create Employee */}
      {showCreate && (
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 max-w-md space-y-3">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Add Employee</h2>
          <div className="grid grid-cols-2 gap-2">
            <input value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="First name" className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white" />
            <input value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder="Last name" className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white" />
          </div>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" type="email" className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white" />
          <div className="grid grid-cols-2 gap-2">
            <input value={position} onChange={(e) => setPosition(e.target.value)} placeholder="Position" className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white" />
            <input value={department} onChange={(e) => setDepartment(e.target.value)} placeholder="Department" className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white" />
          </div>
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowCreate(false)} className="px-4 py-1.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 text-xs">Cancel</button>
            <button onClick={() => createEmployee.mutate()} disabled={!firstName.trim() || !lastName.trim() || !email.trim()} className="px-4 py-1.5 rounded bg-violet-600 text-white text-xs disabled:opacity-50">Add</button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800">
        {(["employees", "leaves", "reviews"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-xs font-medium border-b-2 transition capitalize ${
              activeTab === tab ? "border-violet-600 text-violet-600" : "border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
            }`}
          >
            {tab} ({tab === "employees" ? employees.length : tab === "leaves" ? leaves.length : reviews.length})
          </button>
        ))}
      </div>

      {/* Employees */}
      {activeTab === "employees" && (
        <div className="space-y-2">
          {employees.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">No employees yet. Add your first team member.</div>
          ) : (
            employees.map((emp: any) => (
              <div key={emp.id} className="flex items-center justify-between p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-violet-500/40 transition group">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-violet-500/10 flex items-center justify-center text-violet-500 font-bold text-xs">
                    {emp.first_name[0]}{emp.last_name[0]}
                  </div>
                  <div>
                    <span className="font-medium text-slate-800 dark:text-slate-200 text-xs block">{emp.first_name} {emp.last_name}</span>
                    <span className="text-[10px] text-slate-500">{emp.position || "—"} · {emp.department || "—"}</span>
                  </div>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${STATUS_COLORS[emp.status] || ""}`}>{emp.status.replace("_", " ")}</span>
              </div>
            ))
          )}
        </div>
      )}

      {/* Leaves */}
      {activeTab === "leaves" && (
        <div className="space-y-2">
          {leaves.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">No leave requests.</div>
          ) : (
            leaves.map((leave: any) => (
              <div key={leave.id} className="flex items-center justify-between p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                <div>
                  <span className="font-medium text-slate-800 dark:text-slate-200 text-xs block">{leave.leave_type.replace("_", " ")} leave</span>
                  <span className="text-[10px] text-slate-500">{leave.start_date} → {leave.end_date} ({leave.days} days)</span>
                  {leave.reason && <p className="text-[10px] text-slate-400 mt-1">{leave.reason}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${STATUS_COLORS[leave.status] || ""}`}>{leave.status}</span>
                  {leave.status === "pending" && (
                    <div className="flex gap-1">
                      <button onClick={() => approveLeave.mutate(leave.id)} className="p-1 rounded bg-green-500/10 text-green-500 hover:bg-green-500/20"><Check className="w-3.5 h-3.5" /></button>
                      <button onClick={() => rejectLeave.mutate(leave.id)} className="p-1 rounded bg-red-500/10 text-red-500 hover:bg-red-500/20"><X className="w-3.5 h-3.5" /></button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Reviews */}
      {activeTab === "reviews" && (
        <div className="space-y-2">
          {reviews.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">No performance reviews yet.</div>
          ) : (
            reviews.map((review: any) => (
              <div key={review.id} className="p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-slate-800 dark:text-slate-200">{review.review_period}</span>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star key={i} className={`w-3 h-3 ${i < review.rating ? "text-amber-400 fill-amber-400" : "text-slate-300 dark:text-slate-700"}`} />
                    ))}
                  </div>
                </div>
                {review.comments && <p className="text-[10px] text-slate-500">{review.comments}</p>}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}