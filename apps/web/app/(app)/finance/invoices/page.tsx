"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Receipt, Plus, Eye, DollarSign, Send, CheckCircle2 } from "lucide-react";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-slate-500/10 text-slate-400",
  sent: "bg-blue-500/10 text-blue-400",
  paid: "bg-emerald-500/10 text-emerald-400",
  overdue: "bg-red-500/10 text-red-400",
  cancelled: "bg-slate-800 text-slate-600",
};

export default function InvoicesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [showCreate, setShowCreate] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  // Create invoice form state
  const [invItems, setInvItems] = useState([{ description: "Software Development Services", quantity: "1", unit_price: "5000" }]);
  const [invNotes, setInvNotes] = useState("");
  const [invDueDate, setInvDueDate] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["invoices", filterStatus],
    queryFn: () => {
      const params = new URLSearchParams();
      if (filterStatus) params.set("status", filterStatus);
      return apiClient(`/api/v1/finance/invoices?${params}`).then((r: any) => r);
    },
  });

  const invoices = data?.data || [];

  const createInvoice = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/finance/invoices", {
        method: "POST",
        body: JSON.stringify({
          notes: invNotes || null,
          due_date: invDueDate || null,
          items: invItems.map((it, i) => ({
            description: it.description,
            quantity: parseFloat(it.quantity) || 1,
            unit_price: parseFloat(it.unit_price) || 0,
            amount: (parseFloat(it.quantity) || 1) * (parseFloat(it.unit_price) || 0),
            sort_order: i,
          })),
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      toast.success("Invoice created!");
      setShowCreate(false);
      setInvItems([{ description: "", quantity: "1", unit_price: "" }]);
      setInvNotes("");
      setInvDueDate("");
    },
  });

  const markPaid = useMutation({
    mutationFn: (invoiceId: string) => {
      const inv = invoices.find((i: any) => i.id === invoiceId);
      return apiClient("/api/v1/finance/payments", {
        method: "POST",
        body: JSON.stringify({ invoice_id: invoiceId, amount: inv?.total || 0, payment_method: "manual" }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      queryClient.invalidateQueries({ queryKey: ["finance-dashboard"] });
      toast.success("Payment recorded!");
    },
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Invoices</h1>
          <p className="text-xs text-slate-500 mt-0.5">Create, send, and track invoice payments</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition"
        >
          <Plus className="w-3.5 h-3.5" /> New Invoice
        </button>
      </div>

      {/* Status Filters */}
      <div className="flex gap-2">
        {[null, "draft", "sent", "paid", "overdue"].map((s) => (
          <button
            key={s ?? "all"}
            onClick={() => setFilterStatus(s)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition ${
              filterStatus === s ? "bg-violet-600/20 text-violet-300 border border-violet-500/40" : "text-slate-400 hover:bg-slate-900"
            }`}
          >
            {s ?? "All"}
          </button>
        ))}
      </div>

      {/* Create Invoice Form */}
      {showCreate && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 max-w-2xl">
          <h2 className="text-sm font-semibold text-white">Create New Invoice</h2>

          {/* Line Items */}
          <div className="space-y-2">
            <label className="text-[11px] font-semibold text-slate-500 uppercase">Line Items</label>
            {invItems.map((item, idx) => (
              <div key={idx} className="grid grid-cols-[1fr_80px_100px] gap-2">
                <input value={item.description} onChange={(e) => { const c = [...invItems]; c[idx].description = e.target.value; setInvItems(c); }} placeholder="Description" className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs" />
                <input value={item.quantity} onChange={(e) => { const c = [...invItems]; c[idx].quantity = e.target.value; setInvItems(c); }} placeholder="Qty" className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-center" />
                <input value={item.unit_price} onChange={(e) => { const c = [...invItems]; c[idx].unit_price = e.target.value; setInvItems(c); }} placeholder="Rate" className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-right" />
              </div>
            ))}
            <button onClick={() => setInvItems([...invItems, { description: "", quantity: "1", unit_price: "" }])} className="text-xs text-violet-400 hover:text-violet-300">+ Add line item</button>
          </div>

          <input type="date" value={invDueDate} onChange={(e) => setInvDueDate(e.target.value)} className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs w-48" />
          <textarea value={invNotes} onChange={(e) => setInvNotes(e.target.value)} placeholder="Notes (optional)" rows={2} className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs resize-none" />

          <div className="flex justify-between items-center pt-2 border-t border-slate-800">
            <p className="text-sm font-bold text-white">
              Total: ${invItems.reduce((s, it) => s + (parseFloat(it.quantity) || 1) * (parseFloat(it.unit_price) || 0), 0).toLocaleString()}
            </p>
            <div className="flex gap-2">
              <button onClick={() => setShowCreate(false)} className="px-4 py-1.5 rounded bg-slate-800 text-slate-400 text-xs">Cancel</button>
              <button onClick={() => createInvoice.mutate()} className="px-4 py-1.5 rounded bg-violet-600 text-white text-xs">Create Invoice</button>
            </div>
          </div>
        </div>
      )}

      {/* Invoice List */}
      <div className="border border-slate-800 rounded-xl overflow-hidden text-xs">
        <table className="w-full">
          <thead className="bg-slate-900/60 border-b border-slate-800">
            <tr>
              <th className="text-left px-4 py-3 text-slate-500 font-semibold">Invoice #</th>
              <th className="text-left px-4 py-3 text-slate-500 font-semibold">Status</th>
              <th className="text-left px-4 py-3 text-slate-500 font-semibold">Issue Date</th>
              <th className="text-left px-4 py-3 text-slate-500 font-semibold">Due Date</th>
              <th className="text-right px-4 py-3 text-slate-500 font-semibold">Total</th>
              <th className="text-right px-4 py-3 text-slate-500 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {invoices.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-500">No invoices found.</td></tr>
            ) : (
              invoices.map((inv: any) => (
                <tr key={inv.id} className="hover:bg-slate-900/40 transition">
                  <td className="px-4 py-3 font-mono font-bold text-slate-200">{inv.invoice_number}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-semibold ${STATUS_COLORS[inv.status] || ""}`}>{inv.status}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-400">{inv.issue_date || "—"}</td>
                  <td className="px-4 py-3 text-slate-400">{inv.due_date || "—"}</td>
                  <td className="px-4 py-3 text-right font-bold text-white">${Number(inv.total || 0).toLocaleString()}</td>
                  <td className="px-4 py-3 text-right">
                    {inv.status !== "paid" && (
                      <button onClick={() => markPaid.mutate(inv.id)} className="px-2.5 py-1 rounded bg-emerald-600/20 text-emerald-400 text-[10px] font-semibold hover:bg-emerald-600/30 transition">
                        Mark Paid
                      </button>
                    )}
                    {inv.status === "paid" && <CheckCircle2 className="w-4 h-4 text-emerald-400 inline" />}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
