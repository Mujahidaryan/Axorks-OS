"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { User, Building2, LayoutGrid, Shield, Users, Keyboard } from "lucide-react";

const SETTINGS_NAV = [
  { name: "Profile", href: "/settings/profile", icon: User },
  { name: "Organization", href: "/settings/organization", icon: Building2 },
  { name: "Workspaces", href: "/settings/workspace", icon: LayoutGrid },
  { name: "Team & Roles", href: "/settings/team", icon: Users },
  { name: "Security & 2FA", href: "/settings/security", icon: Shield },
  { name: "Keyboard Shortcuts", href: "/settings/shortcuts", icon: Keyboard },
];

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold tracking-tight">Settings</h1>
        <p className="text-slate-500 text-xs mt-1">
          Manage your personal account, organization, and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <nav className="space-y-1">
          {SETTINGS_NAV.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition",
                  isActive
                    ? "bg-violet-600/10 text-violet-600 dark:text-violet-400 font-semibold"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900"
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="md:col-span-3 glass p-6 rounded-xl border border-slate-200 dark:border-slate-800">
          {children}
        </div>
      </div>
    </div>
  );
}
