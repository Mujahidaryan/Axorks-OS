"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ShieldCheck, Lock, Mail, ArrowRight } from "lucide-react";

export default function PortalLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("client@acme.com");
  const [password, setPassword] = useState("clientsecret123");

  const loginMutation = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/portal/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    onSuccess: (res: any) => {
      toast.success("Welcome to Client Portal!");
      router.push("/portal");
    },
    onError: () => {
      toast.error("Invalid credentials");
    },
  });

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm p-8 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-6 shadow-2xl">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-700 mx-auto flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-violet-600/30">
            AX
          </div>
          <h1 className="text-lg font-bold text-white">Client Portal Login</h1>
          <p className="text-xs text-slate-500">Access project status, proposals, & support tickets</p>
        </div>

        <div className="space-y-3">
          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-400">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs focus:outline-none focus:border-violet-500 text-slate-200"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-400">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs focus:outline-none focus:border-violet-500 text-slate-200"
            />
          </div>

          <button
            onClick={() => loginMutation.mutate()}
            disabled={loginMutation.isPending}
            className="w-full py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs flex items-center justify-center gap-2 transition disabled:opacity-50 mt-4"
          >
            <span>Sign In to Portal</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
