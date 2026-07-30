"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { login } from "@/lib/auth";
import { toast } from "sonner";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await login(email, password);
      if (res.requires_2fa) {
        router.push(`/verify-2fa?user_id=${res.user_id}`);
      } else {
        toast.success("Welcome back to Axorks OS");
        router.push("/");
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to sign in");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass p-8 rounded-2xl shadow-2xl border border-slate-800">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-violet-600/30 text-violet-400 font-bold text-xl mb-4 border border-violet-500/30">
          AX
        </div>
        <h1 className="text-2xl font-bold tracking-tight">Sign in to Axorks OS</h1>
        <p className="text-slate-400 text-sm mt-1">
          Enter your credentials to access your operating system
        </p>
      </div>

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

        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="block text-xs font-medium text-slate-400">
              Password
            </label>
            <Link
              href="/forgot-password"
              className="text-xs text-violet-400 hover:underline"
            >
              Forgot password?
            </Link>
          </div>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••••••"
            className="w-full px-4 py-2.5 bg-slate-900/60 border border-slate-800 rounded-lg text-sm focus:outline-none focus:border-violet-500 transition"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-medium text-sm rounded-lg shadow-lg shadow-violet-600/20 transition disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <div className="text-center mt-6 text-xs text-slate-400">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="text-violet-400 font-medium hover:underline">
          Create one
        </Link>
      </div>
    </div>
  );
}
