"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { ChevronRight } from "lucide-react";

export function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  return (
    <nav className="flex items-center gap-1.5 text-xs text-slate-500">
      <Link href="/" className="hover:text-slate-900 dark:hover:text-slate-100 transition">
        Home
      </Link>
      {segments.map((segment, idx) => {
        const url = `/${segments.slice(0, idx + 1).join("/")}`;
        const isLast = idx === segments.length - 1;
        const name = segment.charAt(0).toUpperCase() + segment.slice(1);

        return (
          <div key={url} className="flex items-center gap-1.5">
            <ChevronRight className="w-3 h-3 text-slate-400" />
            {isLast ? (
              <span className="font-semibold text-slate-900 dark:text-slate-100">
                {name}
              </span>
            ) : (
              <Link href={url} className="hover:text-slate-900 dark:hover:text-slate-100 transition">
                {name}
              </Link>
            )}
          </div>
        );
      })}
    </nav>
  );
}
