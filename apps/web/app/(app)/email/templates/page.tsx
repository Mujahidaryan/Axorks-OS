"use client";

import { useState } from "react";
import Link from "next/link";
import { EMAIL_TEMPLATES, EmailTemplate } from "@/lib/email/templates";
import { LayoutTemplate, ArrowLeft, Search, Plus, Sparkles, Copy, Check } from "lucide-react";
import { toast } from "sonner";

export default function EmailTemplatesPage() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const filtered = EMAIL_TEMPLATES.filter((t) => {
    const matchesSearch =
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.subject.toLowerCase().includes(search.toLowerCase()) ||
      t.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === "all" || t.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleCopySubject = (subject: string, id: string) => {
    navigator.clipboard.writeText(subject);
    setCopiedId(id);
    toast.success("Subject copied to clipboard!");
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            href="/email"
            className="p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <LayoutTemplate className="w-6 h-6 text-violet-600 dark:text-violet-400" /> Email Templates Gallery
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              11 Pre-designed, professional email templates across sales, projects, finance, and support.
            </p>
          </div>
        </div>

        <Link
          href="/email/compose"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-700 text-white font-bold text-xs shadow-md shadow-violet-600/30 transition"
        >
          <Plus className="w-4 h-4" /> Use in Composer
        </Link>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search templates..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
          {["all", "sales", "projects", "finance", "support", "general"].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`text-xs capitalize px-3 py-1.5 rounded-md transition ${
                selectedCategory === cat
                  ? "bg-violet-600 text-white font-semibold"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Template Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((t) => (
          <div
            key={t.id}
            className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between space-y-4 hover:border-violet-500 dark:hover:border-violet-500 transition group"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-sm text-slate-900 dark:text-slate-100 group-hover:text-violet-600 dark:group-hover:text-violet-400 transition">
                  {t.name}
                </span>
                <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 rounded bg-violet-50 dark:bg-violet-950 text-violet-700 dark:text-violet-300">
                  {t.category}
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">{t.description}</p>

              <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs font-mono text-slate-700 dark:text-slate-300 flex items-center justify-between">
                <span className="truncate pr-2">Subject: {t.subject}</span>
                <button
                  type="button"
                  onClick={() => handleCopySubject(t.subject, t.id)}
                  className="text-slate-400 hover:text-violet-600 dark:hover:text-violet-400 p-1"
                >
                  {copiedId === t.id ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">Resend Compliant HTML</span>
              <Link
                href={`/email/compose?template=${t.id}`}
                className="text-xs font-bold text-violet-600 hover:underline flex items-center gap-1"
              >
                Apply & Compose →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
