"""GitHub OAuth callback — wrapped in Suspense for useSearchParams."""

import { Suspense } from "react";
import DevOAuthCallbackInner from "./callback-inner";

export default function DevOAuthCallbackPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-full text-slate-500 text-sm">Connecting GitHub...</div>}>
      <DevOAuthCallbackInner />
    </Suspense>
  );
}
