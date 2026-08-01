"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Send, CheckCircle2 } from "lucide-react";

interface PublicLeadFormProps {
  title?: string;
  subtitle?: string;
  sourceDetail?: string;
  onSuccess?: () => void;
}

export function PublicLeadForm({
  title = "Get a Project Quote & Discovery Call",
  subtitle = "Tell us about your project requirements and our engineering team will get back to you within 24 hours.",
  sourceDetail = "Website Contact Form",
  onSuccess,
}: PublicLeadFormProps) {
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [company, setCompany] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("/api/leads/public-capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision_maker_name: name,
          email,
          phone,
          business_name: company,
          notes: message,
          source: "website",
          source_detail: sourceDetail,
        }),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Failed to submit lead");
      }

      setSubmitted(true);
      toast.success("Thank you! Your inquiry has been received.");
      if (onSuccess) onSuccess();
    } catch (err: any) {
      toast.error(err.message || "Failed to submit inquiry");
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="glass p-8 rounded-2xl border border-emerald-500/30 text-center space-y-4 max-w-lg mx-auto">
        <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
        <h3 className="text-lg font-bold text-slate-100">Inquiry Received!</h3>
        <p className="text-xs text-slate-400">
          Thank you for reaching out to Axorks. One of our solution architects will review your project details and contact you shortly.
        </p>
      </div>
    );
  }

  return (
    <div className="glass p-6 md:p-8 rounded-2xl border border-slate-800 space-y-6 max-w-lg mx-auto">
      <div>
        <h3 className="text-lg font-bold tracking-tight text-slate-100">{title}</h3>
        <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 text-xs">
        <div>
          <label className="block font-medium text-slate-400 mb-1">Your Name *</label>
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Alex Smith"
            className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg focus:outline-none focus:border-violet-500 text-slate-200"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block font-medium text-slate-400 mb-1">Email Address *</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@company.com"
              className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg focus:outline-none focus:border-violet-500 text-slate-200"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-400 mb-1">Phone Number</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+1 (555) 000-0000"
              className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg focus:outline-none focus:border-violet-500 text-slate-200"
            />
          </div>
        </div>

        <div>
          <label className="block font-medium text-slate-400 mb-1">Company / Organization</label>
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="Acme Innovations"
            className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg focus:outline-none focus:border-violet-500 text-slate-200"
          />
        </div>

        <div>
          <label className="block font-medium text-slate-400 mb-1">Project Details / Message *</label>
          <textarea
            required
            rows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Describe your scope of work, technical stack, or project goals..."
            className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg focus:outline-none focus:border-violet-500 text-slate-200"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 bg-violet-600 hover:bg-violet-500 text-white font-medium rounded-lg transition shadow-lg shadow-violet-600/20 flex items-center justify-center gap-2 text-xs disabled:opacity-50"
        >
          <Send className="w-3.5 h-3.5" />
          {loading ? "Submitting Inquiry..." : "Submit Inquiry"}
        </button>
      </form>
    </div>
  );
}
