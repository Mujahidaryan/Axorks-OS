"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { X, Plus } from "lucide-react";

interface LeadCreateDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function LeadCreateDialog({ open, onClose, onSuccess }: LeadCreateDialogProps) {
  const [loading, setLoading] = useState(false);
  const [businessName, setBusinessName] = useState("");
  const [decisionMakerName, setDecisionMakerName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [source, setSource] = useState("manual");
  const [status, setStatus] = useState("new");

  if (!open) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient("/api/v1/leads", {
        method: "POST",
        body: JSON.stringify({
          business_name: businessName,
          decision_maker_name: decisionMakerName,
          email,
          phone,
          source,
          status,
        }),
      });
      toast.success("Lead created successfully");
      onSuccess();
      onClose();
    } catch (err: any) {
      toast.error(err.message || "Failed to create lead");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg glass p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <h2 className="text-base font-semibold">New Lead</h2>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="block font-medium text-slate-400 mb-1">
              Business / Company Name (Optional)
            </label>
            <input
              type="text"
              value={businessName}
              onChange={(e) => setBusinessName(e.target.value)}
              placeholder="Acme Corp"
              className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-400 mb-1">
                Decision Maker Name
              </label>
              <input
                type="text"
                value={decisionMakerName}
                onChange={(e) => setDecisionMakerName(e.target.value)}
                placeholder="Jane Doe"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-400 mb-1">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane@acme.com"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-400 mb-1">Source</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500 text-slate-200"
              >
                <option value="manual">Manual</option>
                <option value="linkedin">LinkedIn</option>
                <option value="website">Website</option>
                <option value="referral">Referral</option>
                <option value="cold_email">Cold Email</option>
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-400 mb-1">Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500 text-slate-200"
              >
                <option value="new">New</option>
                <option value="contacted">Contacted</option>
                <option value="qualified">Qualified</option>
                <option value="proposal">Proposal</option>
              </select>
            </div>
          </div>

          <div className="pt-2 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded bg-violet-600 hover:bg-violet-500 text-white font-medium disabled:opacity-50"
            >
              {loading ? "Saving..." : "Save Lead"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
