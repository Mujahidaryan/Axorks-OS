"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Target, Users, FolderKanban, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

const MOBILE_NAV_ITEMS = [
  { name: "Home", href: "/", icon: LayoutDashboard },
  { name: "IAM", href: "/iam", icon: ShieldCheck },
  { name: "Leads", href: "/leads", icon: Target },
  { name: "CRM", href: "/crm/companies", icon: Users },
  { name: "Projects", href: "/projects", icon: FolderKanban },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/90 dark:bg-slate-950/90 backdrop-blur-xl border-t border-slate-200 dark:border-slate-800">
      <div className="flex items-center justify-around h-14 px-2">
        {MOBILE_NAV_ITEMS.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex flex-col items-center justify-center gap-0.5 px-3 py-1 rounded-lg transition flex-1",
                isActive
                  ? "text-violet-600 dark:text-violet-400"
                  : "text-slate-400 dark:text-slate-600"
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[9px] font-medium">{item.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}