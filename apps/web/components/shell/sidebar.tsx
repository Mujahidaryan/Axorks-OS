"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUIStore } from "@/stores/ui-store";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Target,
  Users,
  FileText,
  FolderKanban,
  Code2,
  Receipt,
  BookOpen,
  Megaphone,
  UserCheck,
  Building2,
  Zap,
  BarChart3,
  Plug,
  Mail,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const NAV_ITEMS = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Leads", href: "/leads", icon: Target },
  {
    name: "CRM",
    href: "/crm/companies",
    icon: Users,
    children: [
      { name: "Companies", href: "/crm/companies", icon: Building2 },
      { name: "Contacts", href: "/crm/contacts", icon: UserCheck },
      { name: "Deals", href: "/crm/deals", icon: Receipt },
    ],
  },
  { name: "Email Center", href: "/email", icon: Mail },
  { name: "Proposals", href: "/proposals", icon: FileText },
  { name: "Projects", href: "/projects", icon: FolderKanban },
  { name: "Dev Hub", href: "/dev", icon: Code2 },
  { name: "Finance", href: "/finance", icon: Receipt },
  { name: "Knowledge", href: "/knowledge", icon: BookOpen },
  { name: "Marketing", href: "/marketing", icon: Megaphone },
  { name: "Recruitment", href: "/recruitment", icon: UserCheck },
  { name: "HR", href: "/hr", icon: Building2 },
  { name: "Automations", href: "/automations", icon: Zap },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Integrations", href: "/integrations", icon: Plug },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        "hidden md:flex h-screen sticky top-0 border-r border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-950/70 backdrop-blur-xl transition-all duration-300 z-30 flex-col justify-between",
        sidebarCollapsed ? "w-16" : "w-64"
      )}
    >
      <div>
        {/* Header / Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-200 dark:border-slate-800">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center text-white font-bold text-sm shadow-md shadow-violet-600/30">
              AX
            </div>
            {!sidebarCollapsed && (
              <span className="font-bold tracking-tight text-slate-900 dark:text-slate-100 text-base">
                Axorks OS
              </span>
            )}
          </Link>

          <button
            onClick={toggleSidebar}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          >
            {sidebarCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-2 space-y-1 overflow-y-auto max-h-[calc(100vh-8rem)]">
          {NAV_ITEMS.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/" && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition group",
                  isActive
                    ? "bg-violet-600 text-white shadow-md shadow-violet-600/20 font-semibold"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-100"
                )}
                title={sidebarCollapsed ? item.name : undefined}
              >
                <Icon className={cn("w-4 h-4 shrink-0", isActive ? "text-white" : "text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200")} />
                {!sidebarCollapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer / Settings */}
      <div className="p-2 border-t border-slate-200 dark:border-slate-800">
        <Link
          href="/settings/profile"
          className={cn(
            "flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-100 transition",
            pathname.startsWith("/settings") && "bg-violet-600 text-white font-semibold"
          )}
          title={sidebarCollapsed ? "Settings" : undefined}
        >
          <Settings className="w-4 h-4 text-slate-400" />
          {!sidebarCollapsed && <span>Settings</span>}
        </Link>
      </div>
    </aside>
  );
}
