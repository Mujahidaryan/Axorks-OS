"use client";

import { cn } from "@/lib/utils";
import { Sparkles } from "lucide-react";

interface AIScoreBadgeProps {
  score: number;
  showIcon?: boolean;
}

export function AIScoreBadge({ score, showIcon = true }: AIScoreBadgeProps) {
  let colorClass = "bg-slate-500/10 text-slate-400 border-slate-500/20";

  if (score >= 75) {
    colorClass = "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30";
  } else if (score >= 50) {
    colorClass = "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30";
  } else if (score > 0) {
    colorClass = "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30";
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border",
        colorClass
      )}
      title={`Quality Score: ${score}/100`}
    >
      {showIcon && <Sparkles className="w-3 h-3" />}
      <span>{score}</span>
    </span>
  );
}
