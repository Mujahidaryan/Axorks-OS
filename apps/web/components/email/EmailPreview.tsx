"use client";

import { useState } from "react";
import { Eye, Monitor, Smartphone, Code, FileText, X } from "lucide-react";

interface EmailPreviewProps {
  to: string[];
  cc: string[];
  bcc: string[];
  subject: string;
  html: string;
  from?: string;
}

export function EmailPreview({ to, cc, bcc, subject, html, from = "hello@axorks.com" }: EmailPreviewProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [viewMode, setViewMode] = useState<"desktop" | "mobile" | "code" | "plain">("desktop");

  const stripHtml = (htmlString: string) => {
    return htmlString.replace(/<[^>]*>?/gm, "").trim();
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition"
      >
        <Eye className="w-3.5 h-3.5 text-blue-500" />
        Preview
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
            {/* Header / Tabs */}
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-slate-900 dark:text-slate-100">Email Preview</span>
                <span className="text-xs bg-violet-100 dark:bg-violet-950 text-violet-700 dark:text-violet-300 px-2 py-0.5 rounded font-mono">
                  {from}
                </span>
              </div>

              {/* View mode toggle */}
              <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
                <button
                  type="button"
                  onClick={() => setViewMode("desktop")}
                  className={`p-1.5 rounded text-xs flex items-center gap-1 transition ${
                    viewMode === "desktop"
                      ? "bg-white dark:bg-slate-900 text-violet-600 font-semibold shadow-sm"
                      : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
                  }`}
                >
                  <Monitor className="w-3.5 h-3.5" /> Desktop
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode("mobile")}
                  className={`p-1.5 rounded text-xs flex items-center gap-1 transition ${
                    viewMode === "mobile"
                      ? "bg-white dark:bg-slate-900 text-violet-600 font-semibold shadow-sm"
                      : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
                  }`}
                >
                  <Smartphone className="w-3.5 h-3.5" /> Mobile
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode("code")}
                  className={`p-1.5 rounded text-xs flex items-center gap-1 transition ${
                    viewMode === "code"
                      ? "bg-white dark:bg-slate-900 text-violet-600 font-semibold shadow-sm"
                      : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
                  }`}
                >
                  <Code className="w-3.5 h-3.5" /> HTML Code
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode("plain")}
                  className={`p-1.5 rounded text-xs flex items-center gap-1 transition ${
                    viewMode === "plain"
                      ? "bg-white dark:bg-slate-900 text-violet-600 font-semibold shadow-sm"
                      : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" /> Plain Text
                </button>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Email Header Info */}
            <div className="p-4 bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 text-xs space-y-1">
              <div>
                <span className="font-semibold text-slate-500">From:</span> {from}
              </div>
              <div>
                <span className="font-semibold text-slate-500">To:</span> {to.join(", ") || "(No recipient)"}
              </div>
              {cc.length > 0 && (
                <div>
                  <span className="font-semibold text-slate-500">CC:</span> {cc.join(", ")}
                </div>
              )}
              {bcc.length > 0 && (
                <div>
                  <span className="font-semibold text-slate-500">BCC:</span> {bcc.join(", ")}
                </div>
              )}
              <div className="font-bold text-slate-900 dark:text-slate-100 pt-1 text-sm">
                Subject: {subject || "(No subject)"}
              </div>
            </div>

            {/* Content Body */}
            <div className="flex-1 overflow-y-auto p-6 flex justify-center bg-slate-100 dark:bg-slate-950/80">
              {viewMode === "desktop" && (
                <div className="bg-white text-slate-900 p-8 rounded-lg shadow-md w-full max-w-2xl min-h-[350px] border border-slate-200 prose prose-slate">
                  <div dangerouslySetInnerHTML={{ __html: html || "<p class='text-slate-400 italic'>No body content</p>" }} />
                </div>
              )}

              {viewMode === "mobile" && (
                <div className="bg-white text-slate-900 p-5 rounded-3xl shadow-xl w-[320px] min-h-[480px] border-4 border-slate-800 prose prose-slate text-xs overflow-y-auto">
                  <div dangerouslySetInnerHTML={{ __html: html || "<p class='text-slate-400 italic'>No body content</p>" }} />
                </div>
              )}

              {viewMode === "code" && (
                <pre className="w-full bg-slate-900 text-slate-100 p-4 rounded-lg text-xs font-mono overflow-x-auto">
                  <code>{html}</code>
                </pre>
              )}

              {viewMode === "plain" && (
                <div className="w-full bg-white dark:bg-slate-900 p-6 rounded-lg text-xs text-slate-800 dark:text-slate-200 whitespace-pre-wrap font-mono border border-slate-200 dark:border-slate-800">
                  {stripHtml(html) || "No content"}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
