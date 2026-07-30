"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { setAccessToken } from "@/lib/auth";
import { toast } from "sonner";

export default function Verify2FAPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const userId = searchParams.get("user_id");

  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId) return;
    setLoading(true);
    try {
      const data = await apiClient(`/api/v1/auth/login/2fa?user_id=${userId}`, {
        method: "POST",
        body: JSON.stringify({ code }),
      });
      if (data.access_token) {
        setAccessToken(data.access_token);
        toast.success("2FA verified");
        router.push("/");
      }
    } catch (err: any) {
      toast.error(err.message || "Invalid 2FA code");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass p-8 rounded-2xl shadow-2xl border border-slate-800 text-center">
      <h1 className="text-2xl font-bold tracking-tight mb-2">Two-Factor Auth</h1>
      <p className="text-slate-400 text-sm mb-6">
        Enter the 6-digit code from your authenticator app
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          maxLength={6}
          required
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="123456"
          className="w-full text-center text-2xl tracking-widest py-3 bg-slate-900/60 border border-slate-800 rounded-lg focus:outline-none focus:border-violet-500 font-mono"
        />

        <button
          type="submit"
          disabled={loading || code.length !== 6}
          className="w-full py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-medium text-sm rounded-lg transition disabled:opacity-50"
        >
          {loading ? "Verifying..." : "Verify Code"}
        </button>
      </form>
    </div>
  );
}
