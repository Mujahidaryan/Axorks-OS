"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

export default function DevOAuthCallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) {
      setStatus("error");
      toast.error("OAuth callback missing authorization code");
      return;
    }

    apiClient("/api/v1/dev/oauth/github/callback", {
      method: "POST",
      body: JSON.stringify({ code }),
    })
      .then(() => {
        setStatus("success");
        toast.success("GitHub connected successfully!");
        setTimeout(() => router.replace("/dev"), 1500);
      })
      .catch((err: Error) => {
        setStatus("error");
        toast.error(err.message || "GitHub OAuth failed");
      });
  }, [searchParams, router]);

  return (
    <div className="flex flex-col items-center justify-center h-full gap-3 text-sm text-slate-400">
      {status === "loading" && (
        <>
          <Loader2 className="w-6 h-6 animate-spin text-violet-400" />
          <p>Connecting GitHub account...</p>
        </>
      )}
      {status === "success" && <p className="text-emerald-400">GitHub connected! Redirecting...</p>}
      {status === "error" && (
        <button onClick={() => router.push("/dev")} className="text-violet-400 hover:underline text-xs">
          Return to Dev Hub
        </button>
      )}
    </div>
  );
}
