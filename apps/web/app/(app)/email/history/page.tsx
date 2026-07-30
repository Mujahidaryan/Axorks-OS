"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { History, ArrowLeft, Search, CheckCircle2, XCircle, Clock, Eye, X } from "lucide-react";

export default function EmailHistoryPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedMessage, setSelectedMessage] = useState<any | null>(null);

  useEffect(() => {
    fetchLogs();
  }, [search, statusFilter]);

  async function fetchLogs() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (statusFilter) params.set("status", statusFilter);

      const res = await fetch(`/api/email/history?${params.toString()}`);
      const json = await res.json();
      if (json.success) {
        setData(json.data);
      }
    } catch (e) {
      console.error("Failed to fetch email logs", e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/email"
            className="p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <History className="w-6 h-6 text-violet-600 dark:text-violet-400" /> Email History & Delivery Logs
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Audit logs, message IDs, and status tracking for all emails sent via Resend API.
            </p>
          </div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by recipient, subject, sender..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 text-slate-700 dark:text-slate-300 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="sent">Sent</option>
            <option value="failed">Failed</option>
            <option value="queued">Queued</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <div className="p-5 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
        {loading ? (
          <div className="py-12 text-center text-xs text-slate-400">Loading delivery logs...</div>
        ) : data.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400">No email records found matching your filters.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-950 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="p-3">Recipient</th>
                  <th className="p-3">Subject</th>
                  <th className="p-3">Message ID</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Provider</th>
                  <th className="p-3">Sent At</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {data.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition">
                    <td className="p-3 font-semibold text-slate-800 dark:text-slate-200">{item.recipient}</td>
                    <td className="p-3 text-slate-600 dark:text-slate-300 max-w-xs truncate">{item.subject}</td>
                    <td className="p-3 font-mono text-[11px] text-slate-500">{item.messageId}</td>
                    <td className="p-3">
                      <span
                        className={`inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                          item.status === "Sent"
                            ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300"
                            : item.status === "Failed"
                            ? "bg-red-50 text-red-700 dark:bg-red-950/60 dark:text-red-300"
                            : "bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300"
                        }`}
                      >
                        {item.status === "Sent" ? (
                          <CheckCircle2 className="w-3 h-3" />
                        ) : item.status === "Failed" ? (
                          <XCircle className="w-3 h-3" />
                        ) : (
                          <Clock className="w-3 h-3" />
                        )}
                        {item.status}
                      </span>
                    </td>
                    <td className="p-3 font-medium text-slate-500">{item.provider || "Resend"}</td>
                    <td className="p-3 text-slate-400">{new Date(item.createdAt).toLocaleString()}</td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => setSelectedMessage(item)}
                        className="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-violet-600 transition"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Message Log Detail Modal */}
      {selectedMessage && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <h3 className="font-bold text-sm text-slate-900 dark:text-slate-100">Delivery Log Details</h3>
              <button onClick={() => setSelectedMessage(null)} className="text-slate-400 hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 space-y-3 text-xs">
              <div>
                <span className="font-semibold text-slate-500">Message ID:</span>{" "}
                <span className="font-mono text-slate-800 dark:text-slate-200">{selectedMessage.messageId}</span>
              </div>
              <div>
                <span className="font-semibold text-slate-500">Recipient:</span> {selectedMessage.recipient}
              </div>
              <div>
                <span className="font-semibold text-slate-500">Subject:</span> {selectedMessage.subject}
              </div>
              <div>
                <span className="font-semibold text-slate-500">Provider:</span> {selectedMessage.provider}
              </div>
              <div>
                <span className="font-semibold text-slate-500">Delivery Status:</span> {selectedMessage.deliveryStatus}
              </div>
              <div>
                <span className="font-semibold text-slate-500">Sent By:</span> {selectedMessage.sentBy}
              </div>
              <div>
                <span className="font-semibold text-slate-500">Timestamp:</span>{" "}
                {new Date(selectedMessage.createdAt).toString()}
              </div>

              {selectedMessage.error && (
                <div className="p-3 bg-red-50 dark:bg-red-950/50 text-red-700 dark:text-red-300 rounded-lg text-xs font-mono">
                  Error: {selectedMessage.error}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
