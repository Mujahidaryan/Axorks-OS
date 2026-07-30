"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { register } from "@/lib/auth";
import { toast } from "sonner";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
      });
      toast.success("Account created successfully!");
      router.push("/");
    } catch (err: any) {
      toast.error(err.message || "Failed to create account");
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
        <h1 className="text-2xl font-bold tracking-tight">Create an Account</h1>
        <p className="text-slate-400 text-sm mt-1">
          Set up your workspace on Axorks OS
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              First Name
            </label>
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="Alex"
              className="w-full px-4 py-2.5 bg-slate-900/60 border border-slate-800 rounded-lg text-sm focus:outline-none focus:border-violet-500 transition"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Last Name
            </label>
            <input
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Morgan"
              className="w-full px-4 py-2.5 bg-slate-900/60 border border-slate-800 rounded-lg text-sm focus:outline-none focus:border-violet-500 transition"
            />
          </div>
        </div>

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
          <label className="block text-xs font-medium text-slate-400 mb-1">
            Password (min 12 chars)
          </label>
          <input
            type="password"
            required
            minLength={12}
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
          {loading ? "Creating Account..." : "Create Account"}
        </button>
      </form>

      <div className="text-center mt-6 text-xs text-slate-400">
        Already have an account?{" "}
        <Link href="/login" className="text-violet-400 font-medium hover:underline">
          Sign in
        </Link>
      </div>
    </div>
  );
}
