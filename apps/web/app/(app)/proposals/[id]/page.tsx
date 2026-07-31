"use client";

import { use, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import {
  FileText, Send, Download, Sparkles, Plus, Trash2, Save, Eye, CheckCircle2,
} from "lucide-react";

export default function ProposalDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const queryClient = useQueryClient();

  const { data: proposal, isLoading } = useQuery({
    queryKey: ["proposal", id],
    queryFn: () => apiClient(`/api/v1/proposals/${id}`).then((r: any) => r.data),
    enabled: !!id,
  });

  const [activeTab, setActiveTab] = useState<"edit" | "preview">("edit");
  const [sections, setSections] = useState<any[]>([]);
  const [pricingItems, setPricingItems] = useState<any[]>([]);

  // Sync state when proposal loads
  const content = proposal?.content || {};
  const currentSections = sections.length > 0 ? sections : content.sections || [];
  const currentPricing = pricingItems.length > 0 ? pricingItems : content.pricing?.items || [];

  const updateProposal = useMutation({
    mutationFn: (updates: Record<string, any>) =>
      apiClient(`/api/v1/proposals/${id}`, {
        method: "PATCH",
        body: JSON.stringify(updates),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposal", id] });
      toast.success("Proposal saved");
    },
  });

  const sendProposal = useMutation({
    mutationFn: () => apiClient(`/api/v1/proposals/${id}/send`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposal", id] });
      toast.success("Proposal sent via email");
    },
  });

  const exportPDF = useMutation({
    mutationFn: () => apiClient(`/api/v1/proposals/${id}/export/pdf`, { method: "POST" }),
    onSuccess: (res: any) => {
      toast.success("PDF generated successfully");
      window.open(res.data.pdf_url, "_blank");
    },
  });

  const exportDocx = useMutation({
    mutationFn: () => apiClient(`/api/v1/proposals/${id}/export/docx`, { method: "POST" }),
    onSuccess: (res: any) => {
      toast.success("Word document generated");
      window.open(res.data.docx_url, "_blank");
    },
  });

  if (isLoading || !proposal) {
    return <div className="flex items-center justify-center h-full text-slate-500 text-sm">Loading proposal...</div>;
  }

  const handleSave = () => {
    const updatedContent = {
      ...content,
      sections: currentSections,
      pricing: {
        items: currentPricing,
        subtotal: currentPricing.reduce((sum: number, item: any) => sum + (Number(item.amount) || 0), 0),
        tax: 0,
        total: currentPricing.reduce((sum: number, item: any) => sum + (Number(item.amount) || 0), 0),
      },
    };
    const totalVal = currentPricing.reduce((sum: number, item: any) => sum + (Number(item.amount) || 0), 0);
    updateProposal.mutate({ content: updatedContent, total_value: totalVal });
  };

  return (
    <div className="h-full flex flex-col">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-slate-800 bg-slate-950/60 sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-violet-400" />
          <div>
            <h1 className="text-sm font-bold text-white leading-tight">{proposal.title}</h1>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-[10px] text-slate-500 uppercase font-semibold">{proposal.type.replace("_", " ")}</span>
              <span className="text-[10px] text-slate-600">•</span>
              <span className="text-[10px] text-slate-400">v{proposal.version}</span>
              <span className="text-[10px] text-slate-600">•</span>
              <span className="text-[10px] font-semibold text-emerald-400 capitalize">{proposal.status}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Edit / Preview Toggle */}
          <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setActiveTab("edit")}
              className={`px-3 py-1 rounded-md text-xs font-medium transition ${
                activeTab === "edit" ? "bg-violet-600 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Edit
            </button>
            <button
              onClick={() => setActiveTab("preview")}
              className={`px-3 py-1 rounded-md text-xs font-medium transition ${
                activeTab === "preview" ? "bg-violet-600 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Preview
            </button>
          </div>

          <button onClick={handleSave} disabled={updateProposal.isPending} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium">
            <Save className="w-3.5 h-3.5" /> Save
          </button>

          <button onClick={() => exportPDF.mutate()} disabled={exportPDF.isPending} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium">
            <Download className="w-3.5 h-3.5 text-cyan-400" /> Export PDF
          </button>

          <button onClick={() => exportDocx.mutate()} disabled={exportDocx.isPending} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium">
            <Download className="w-3.5 h-3.5 text-indigo-400" /> Export Word
          </button>

          <button onClick={() => sendProposal.mutate()} disabled={sendProposal.isPending} className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-semibold">
            <Send className="w-3.5 h-3.5" /> Send Proposal
          </button>
        </div>
      </div>

      {/* Main Body */}
      <div className="flex-1 overflow-y-auto p-8 max-w-4xl mx-auto w-full space-y-6">
        {activeTab === "edit" ? (
          <>
            {/* Sections Editor */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Proposal Sections</h2>
                <button
                  onClick={() =>
                    setSections([
                      ...currentSections,
                      { title: "New Section", content: "", order: currentSections.length + 1 },
                    ])
                  }
                  className="flex items-center gap-1 text-xs text-violet-400 hover:underline"
                >
                  <Plus className="w-3 h-3" /> Add Section
                </button>
              </div>

              {currentSections.map((sec: any, idx: number) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <input
                      value={sec.title}
                      onChange={(e) => {
                        const updated = [...currentSections];
                        updated[idx].title = e.target.value;
                        setSections(updated);
                      }}
                      className="bg-transparent font-semibold text-white text-sm focus:outline-none focus:border-violet-500 border-b border-transparent"
                    />
                    <button
                      onClick={() => {
                        const updated = currentSections.filter((_: any, i: number) => i !== idx);
                        setSections(updated);
                      }}
                      className="p-1 text-slate-600 hover:text-red-400"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <textarea
                    value={sec.content}
                    onChange={(e) => {
                      const updated = [...currentSections];
                      updated[idx].content = e.target.value;
                      setSections(updated);
                    }}
                    rows={4}
                    className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 resize-y focus:outline-none focus:border-violet-500 font-mono"
                  />
                </div>
              ))}
            </div>

            {/* Pricing Table Editor */}
            <div className="space-y-4 pt-4 border-t border-slate-800">
              <div className="flex items-center justify-between">
                <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Pricing & Deliverables</h2>
                <button
                  onClick={() =>
                    setPricingItems([
                      ...currentPricing,
                      { description: "New deliverable", quantity: 1, unit_price: 1000, amount: 1000 },
                    ])
                  }
                  className="flex items-center gap-1 text-xs text-violet-400 hover:underline"
                >
                  <Plus className="w-3 h-3" /> Add Line Item
                </button>
              </div>

              <div className="border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-xs">
                  <thead className="bg-slate-900/80 border-b border-slate-800">
                    <tr>
                      <th className="text-left px-4 py-2.5 text-slate-500">Description</th>
                      <th className="text-left px-4 py-2.5 text-slate-500 w-20">Qty</th>
                      <th className="text-left px-4 py-2.5 text-slate-500 w-32">Unit Price ($)</th>
                      <th className="text-left px-4 py-2.5 text-slate-500 w-32">Amount ($)</th>
                      <th className="w-10"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {currentPricing.map((item: any, idx: number) => (
                      <tr key={idx}>
                        <td className="px-4 py-2">
                          <input
                            value={item.description}
                            onChange={(e) => {
                              const updated = [...currentPricing];
                              updated[idx].description = e.target.value;
                              setPricingItems(updated);
                            }}
                            className="w-full bg-transparent text-slate-200 text-xs focus:outline-none"
                          />
                        </td>
                        <td className="px-4 py-2">
                          <input
                            type="number"
                            value={item.quantity}
                            onChange={(e) => {
                              const updated = [...currentPricing];
                              const qty = parseInt(e.target.value) || 0;
                              updated[idx].quantity = qty;
                              updated[idx].amount = qty * (updated[idx].unit_price || 0);
                              setPricingItems(updated);
                            }}
                            className="w-full bg-transparent text-slate-200 text-xs focus:outline-none"
                          />
                        </td>
                        <td className="px-4 py-2">
                          <input
                            type="number"
                            value={item.unit_price}
                            onChange={(e) => {
                              const updated = [...currentPricing];
                              const price = parseFloat(e.target.value) || 0;
                              updated[idx].unit_price = price;
                              updated[idx].amount = (updated[idx].quantity || 0) * price;
                              setPricingItems(updated);
                            }}
                            className="w-full bg-transparent text-slate-200 text-xs focus:outline-none"
                          />
                        </td>
                        <td className="px-4 py-2 font-bold text-slate-200">${Number(item.amount).toLocaleString()}</td>
                        <td className="px-2 py-2">
                          <button
                            onClick={() => {
                              const updated = currentPricing.filter((_: any, i: number) => i !== idx);
                              setPricingItems(updated);
                            }}
                            className="text-slate-600 hover:text-red-400"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          /* Preview Mode Document */
          <div className="bg-white text-slate-900 p-10 rounded-xl shadow-2xl space-y-8 min-h-[800px]">
            <div className="border-b border-slate-200 pb-6 flex justify-between items-start">
              <div>
                <span className="text-xs font-bold text-violet-600 tracking-wider uppercase">AXORKS OS — PROPOSAL</span>
                <h1 className="text-2xl font-bold text-slate-900 mt-1">{proposal.title}</h1>
                <p className="text-xs text-slate-500 mt-0.5">Prepared for client engagement</p>
              </div>
              <div className="text-right text-xs text-slate-500 space-y-0.5">
                <p className="font-semibold text-slate-700">Date: {new Date(proposal.created_at).toLocaleDateString()}</p>
                <p>Valid Until: {proposal.valid_until || "30 Days"}</p>
              </div>
            </div>

            {currentSections.map((sec: any, idx: number) => (
              <div key={idx} className="space-y-2">
                <h2 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-1">{sec.title}</h2>
                <p className="text-xs text-slate-600 whitespace-pre-wrap leading-relaxed">{sec.content}</p>
              </div>
            ))}

            {currentPricing.length > 0 && (
              <div className="space-y-3 pt-4 border-t border-slate-200">
                <h2 className="text-base font-bold text-slate-800">Investment Summary</h2>
                <table className="w-full text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr>
                      <th className="text-left py-2 px-3 text-slate-600 font-semibold">Item Description</th>
                      <th className="text-center py-2 px-3 text-slate-600 font-semibold w-16">Qty</th>
                      <th className="text-right py-2 px-3 text-slate-600 font-semibold w-28">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {currentPricing.map((item: any, idx: number) => (
                      <tr key={idx}>
                        <td className="py-2.5 px-3 text-slate-700">{item.description}</td>
                        <td className="py-2.5 px-3 text-center text-slate-500">{item.quantity}</td>
                        <td className="py-2.5 px-3 text-right font-semibold text-slate-800">${Number(item.amount).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
