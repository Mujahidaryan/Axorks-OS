"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { LifeBuoy, Plus, MessageSquare, Send, CheckCircle2 } from "lucide-react";

export default function PortalSupportPage() {
  const queryClient = useQueryClient();
  const mockCompanyId = "00000000-0000-0000-0000-000000000001";
  const mockPortalUserId = "00000000-0000-0000-0000-000000000002";
  const mockOrgId = "00000000-0000-0000-0000-000000000003";

  const [showCreate, setShowCreate] = useState(false);
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");

  const [activeTicket, setActiveTicket] = useState<any>(null);
  const [replyText, setReplyText] = useState("");

  const { data: tickets = [] } = useQuery({
    queryKey: ["portal-tickets", mockCompanyId],
    queryFn: () => apiClient(`/api/v1/portal/company/${mockCompanyId}/tickets`).then((r: any) => r.data || []),
  });

  const createTicket = useMutation({
    mutationFn: () =>
      apiClient(`/api/v1/portal/company/${mockCompanyId}/tickets?portal_user_id=${mockPortalUserId}&org_id=${mockOrgId}`, {
        method: "POST",
        body: JSON.stringify({ subject, description, priority }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portal-tickets", mockCompanyId] });
      toast.success("Support ticket submitted!");
      setShowCreate(false);
      setSubject("");
      setDescription("");
    },
  });

  const sendReply = useMutation({
    mutationFn: () =>
      apiClient(`/api/v1/portal/tickets/${activeTicket.id}/messages`, {
        method: "POST",
        body: JSON.stringify({ message: replyText }),
      }),
    onSuccess: () => {
      toast.success("Message sent");
      setReplyText("");
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Client Support & Tickets</h1>
          <p className="text-xs text-slate-500 mt-0.5">Submit technical inquiries, bug reports, and change requests.</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition"
        >
          <Plus className="w-3.5 h-3.5" /> Submit New Ticket
        </button>
      </div>

      {showCreate && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 max-w-md space-y-3">
          <h2 className="text-sm font-semibold text-white">New Support Ticket</h2>
          <input
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="Subject summary"
            className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Detailed description of issue or request..."
            rows={3}
            className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs resize-none"
          />
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowCreate(false)} className="px-4 py-1.5 rounded bg-slate-800 text-slate-400 text-xs">Cancel</button>
            <button onClick={() => createTicket.mutate()} disabled={!subject.trim()} className="px-4 py-1.5 rounded bg-violet-600 text-white text-xs disabled:opacity-50">Submit</button>
          </div>
        </div>
      )}

      {/* Tickets List */}
      <div className="space-y-3">
        {tickets.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 border border-slate-800 rounded-xl">No open support tickets.</div>
        ) : (
          tickets.map((t: any) => (
            <div key={t.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white">{t.subject}</span>
                <span className="px-2.5 py-0.5 rounded-full bg-violet-500/10 text-violet-400 font-semibold uppercase text-[10px]">{t.status}</span>
              </div>
              <p className="text-slate-400">{t.description}</p>
              <div className="flex justify-between items-center text-[10px] text-slate-500 pt-2 border-t border-slate-800/60">
                <span>Priority: <strong className="capitalize text-slate-300">{t.priority}</strong></span>
                <span>Submitted {new Date(t.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
