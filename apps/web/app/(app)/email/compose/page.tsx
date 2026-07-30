"use client";

import { ComposeEmail } from "@/components/email/ComposeEmail";
import { ArrowLeft, Mail } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function EmailComposePage() {
  const router = useRouter();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/email"
            className="p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Mail className="w-6 h-6 text-violet-600 dark:text-violet-400" /> Compose Email
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Dispatch professional emails using verified sender hello@axorks.com.
            </p>
          </div>
        </div>
      </div>

      <ComposeEmail onSuccess={() => router.push("/email/history")} />
    </div>
  );
}
