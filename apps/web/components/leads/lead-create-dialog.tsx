"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { X } from "lucide-react";

interface LeadCreateDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function LeadCreateDialog({ open, onClose, onSuccess }: LeadCreateDialogProps) {
  const [loading, setLoading] = useState(false);
  const [businessName, setBusinessName] = useState("");
  const [decisionMakerName, setDecisionMakerName] = useState("");
  const [decisionMakerTitle, setDecisionMakerTitle] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [website, setWebsite] = useState("");
  const [industry, setIndustry] = useState("");
  const [country, setCountry] = useState("");
  const [source, setSource] = useState("manual");
  const [sourceDetail, setSourceDetail] = useState("");
  const [status, setStatus] = useState("new");
  const [notes, setNotes] = useState("");

  if (!open) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient("/api/v1/leads", {
        method: "POST",
        body: JSON.stringify({
          business_name: businessName || null,
          decision_maker_name: decisionMakerName || null,
          decision_maker_title: decisionMakerTitle || null,
          email: email || null,
          phone: phone || null,
          website: website || null,
          industry: industry || null,
          country: country || null,
          source,
          source_detail: sourceDetail || null,
          status,
          notes: notes || null,
        }),
      });
      toast.success("Lead created successfully");
      // Reset form
      setBusinessName("");
      setDecisionMakerName("");
      setDecisionMakerTitle("");
      setEmail("");
      setPhone("");
      setWebsite("");
      setIndustry("");
      setCountry("");
      setSource("manual");
      setSourceDetail("");
      setStatus("new");
      setNotes("");
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
      <div className="w-full max-w-lg glass p-6 rounded-2xl border border-slate-800 space-y-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <h2 className="text-base font-semibold">New Lead</h2>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-400 mb-1">
                Business / Company Name
              </label>
              <input
                type="text"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                placeholder="Acme Corp"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-400 mb-1">
                Website URL
              </label>
              <input
                type="text"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                placeholder="https://acme.com"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
              />
            </div>
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
                Title / Role
              </label>
              <input
                type="text"
                value={decisionMakerTitle}
                onChange={(e) => setDecisionMakerTitle(e.target.value)}
                placeholder="CEO / Director"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
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
            <div>
              <label className="block font-medium text-slate-400 mb-1">
                Phone Number / WhatsApp
              </label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 000-0000"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-400 mb-1">Industry</label>
              <input
                type="text"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="Software / Healthcare"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-400 mb-1">Country</label>
              <input
                type="text"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                placeholder="United States"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-400 mb-1">Lead Source</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500 text-slate-200"
              >
                <option value="manual">Manual Entry</option>
                <option value="cold_call">Phone Call / WhatsApp</option>
                <option value="referral">Referral / Word of Mouth</option>
                <option value="linkedin">LinkedIn</option>
                <option value="instagram">Instagram</option>
                <option value="facebook">Facebook</option>
                <option value="youtube">YouTube</option>
                <option value="website">Website Contact Form</option>
                <option value="cold_email">Email Inquiry / Cold Email</option>
                <option value="google_business">Google Business Profile</option>
                <option value="directory">Business Directory</option>
                <option value="other">Other External Source</option>
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-400 mb-1">Initial Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500 text-slate-200"
              >
                <option value="new">New</option>
                <option value="contacted">Contacted</option>
                <option value="qualified">Qualified</option>
                <option value="proposal">Proposal</option>
                <option value="negotiation">Negotiation</option>
                <option value="won">Won</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-medium text-slate-400 mb-1">
              Source Detail / Reference (Optional)
            </label>
            <input
              type="text"
              value={sourceDetail}
              onChange={(e) => setSourceDetail(e.target.value)}
              placeholder="e.g. WhatsApp message from +123456, Referred by Alex"
              className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-400 mb-1">Notes / Requirements</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              placeholder="Add key notes, requested services, or initial conversation details..."
              className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded focus:outline-none focus:border-violet-500 font-sans"
            />
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
