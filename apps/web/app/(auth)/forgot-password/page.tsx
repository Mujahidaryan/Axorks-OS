"use client";

import { useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient("/api/v1/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setSubmitted(true);
    } catch (err: any) {
      toast.error(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass p-8 rounded-2xl shadow-2xl border border-slate-800">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold tracking-tight">Reset Password</h1>
        <p className="text-slate-400 text-sm mt-1">
          {submitted
            ? "Check your email for reset instructions"
            : "Enter your email to receive a password reset link"}
        </p>
      </div>

      {!submitted ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@axorks.com"
              className="w-full px-4 py-2.5 bg-slate-900/60 border border-slate-800 rounded-lg text-sm focus:outline-none focus:border-violet-500 transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-medium text-sm rounded-lg shadow-lg shadow-violet-600/20 transition disabled:opacity-50"
          >
            {loading ? "Sending..." : "Send Reset Link"}
          </button>
        </form>
      ) : (
        <div className="text-center py-4">
          <p className="text-xs text-slate-300">
            If an account exists for {email}, you will receive a reset link shortly.
          </p>
        </div>
      )}

      <div className="text-center mt-6 text-xs text-slate-400">
        Back to{" "}
        <Link href="/login" className="text-violet-400 font-medium hover:underline">
          Sign in
        </Link>
      </div>
    </div>
  );
}
