"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { UserCheck, Plus, Briefcase, Users, ChevronRight, FileText } from "lucide-react";

const EMPLOYMENT_TYPES = ["full_time", "part_time", "contract", "internship"];
const STATUS_COLORS: Record<string, string> = {
  draft: "bg-slate-500/10 text-slate-400",
  open: "bg-green-500/10 text-green-400",
  closed: "bg-red-500/10 text-red-400",
  applied: "bg-blue-500/10 text-blue-400",
  reviewing: "bg-amber-500/10 text-amber-400",
  interviewed: "bg-violet-500/10 text-violet-400",
  offered: "bg-green-500/10 text-green-400",
  rejected: "bg-red-500/10 text-red-400",
};

export default function RecruitmentPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [department, setDepartment] = useState("");
  const [location, setLocation] = useState("");
  const [employmentType, setEmploymentType] = useState("full_time");
  const [activeTab, setActiveTab] = useState<"jobs" | "applications">("jobs");

  const { data: jobs = [] } = useQuery({
    queryKey: ["recruitment-jobs"],
    queryFn: () => apiClient("/api/v1/recruitment/job-postings"),
  });

  const { data: applications = [] } = useQuery({
    queryKey: ["recruitment-applications"],
    queryFn: () => apiClient("/api/v1/recruitment/applications"),
  });

  const createJob = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/recruitment/job-postings", {
        method: "POST",
        body: JSON.stringify({
          title,
          description,
          department: department || undefined,
          location: location || undefined,
          employment_type: employmentType,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recruitment-jobs"] });
      toast.success("Job posting created!");
      setShowCreate(false);
      setTitle("");
      setDescription("");
      setDepartment("");
      setLocation("");
    },
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Recruitment</h1>
          <p className="text-xs text-slate-500 mt-0.5">Candidate pipeline, job postings, applications & interviews</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition"
        >
          <Plus className="w-3.5 h-3.5" /> New Job Posting
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <Briefcase className="w-4 h-4 text-violet-500 mb-2" />
          <p className="text-2xl font-bold text-slate-900 dark:text-white">{jobs.length}</p>
          <p className="text-[10px] uppercase tracking-wide text-slate-500">Job Postings</p>
        </div>
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <Users className="w-4 h-4 text-blue-500 mb-2" />
          <p className="text-2xl font-bold text-slate-900 dark:text-white">{applications.length}</p>
          <p className="text-[10px] uppercase tracking-wide text-slate-500">Applications</p>
        </div>
      </div>

      {/* Create Job Modal */}
      {showCreate && (
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 max-w-md space-y-3">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Create Job Posting</h2>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Job title"
            className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Job description"
            rows={4}
            className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white"
          />
          <div className="grid grid-cols-2 gap-2">
            <input
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              placeholder="Department"
              className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white"
            />
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Location"
              className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white"
            />
          </div>
          <select
            value={employmentType}
            onChange={(e) => setEmploymentType(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-900 dark:text-white"
          >
            {EMPLOYMENT_TYPES.map((t) => (
              <option key={t} value={t}>{t.replace("_", " ")}</option>
            ))}
          </select>
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowCreate(false)} className="px-4 py-1.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 text-xs">Cancel</button>
            <button
              onClick={() => createJob.mutate()}
              disabled={!title.trim() || !description.trim()}
              className="px-4 py-1.5 rounded bg-violet-600 text-white text-xs disabled:opacity-50"
            >
              Create
            </button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setActiveTab("jobs")}
          className={`px-4 py-2 text-xs font-medium border-b-2 transition ${
            activeTab === "jobs"
              ? "border-violet-600 text-violet-600"
              : "border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
          }`}
        >
          Job Postings ({jobs.length})
        </button>
        <button
          onClick={() => setActiveTab("applications")}
          className={`px-4 py-2 text-xs font-medium border-b-2 transition ${
            activeTab === "applications"
              ? "border-violet-600 text-violet-600"
              : "border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
          }`}
        >
          Applications ({applications.length})
        </button>
      </div>

      {/* Job Postings */}
      {activeTab === "jobs" && (
        <div className="space-y-2">
          {jobs.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">
              No job postings yet. Create your first posting to get started.
            </div>
          ) : (
            jobs.map((job: any) => (
              <div
                key={job.id}
                className="flex items-center justify-between p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 hover:border-violet-500/40 transition cursor-pointer group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                    <Briefcase className="w-4 h-4 text-violet-500" />
                  </div>
                  <div>
                    <span className="font-medium text-slate-800 dark:text-slate-200 text-xs block">{job.title}</span>
                    <span className="text-[10px] text-slate-500">
                      {job.department || "—"} · {job.location || "Remote"} · {job.employment_type.replace("_", " ")}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${STATUS_COLORS[job.status] || ""}`}>
                    {job.status}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-violet-500 transition" />
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Applications */}
      {activeTab === "applications" && (
        <div className="space-y-2">
          {applications.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 border border-slate-200 dark:border-slate-800 rounded-xl">
              No applications received yet.
            </div>
          ) : (
            applications.map((app: any) => (
              <div
                key={app.id}
                className="flex items-center justify-between p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center">
                    <UserCheck className="w-4 h-4 text-slate-500" />
                  </div>
                  <div>
                    <span className="font-medium text-slate-800 dark:text-slate-200 text-xs block">{app.candidate_name}</span>
                    <span className="text-[10px] text-slate-500">{app.candidate_email}</span>
                  </div>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${STATUS_COLORS[app.status] || ""}`}>
                  {app.status}
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}