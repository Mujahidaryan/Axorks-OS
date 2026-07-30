"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, FolderKanban, Receipt, FileText, LifeBuoy, LogOut } from "lucide-react";

export default function ClientPortalLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname === "/portal/login") {
    return <>{children}</>;
  }

  const NAV_ITEMS = [
    { name: "Dashboard", href: "/portal", icon: ShieldCheck },
    { name: "Invoices", href: "/portal/invoices", icon: Receipt },
    { name: "Documents", href: "/portal/documents", icon: FileText },
    { name: "Support", href: "/portal/support", icon: LifeBuoy },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Client Header */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-700 flex items-center justify-center font-bold text-xs text-white">
            AX
          </div>
          <div>
            <span className="font-bold text-sm text-white block leading-tight">Axorks OS</span>
            <span className="text-[10px] text-violet-400 font-semibold tracking-wider uppercase">Client Portal</span>
          </div>
        </div>

        <nav className="flex items-center gap-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  isActive
                    ? "bg-violet-600/20 text-violet-300 border border-violet-500/40"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <Link href="/portal/login" className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-red-400 transition">
          <LogOut className="w-3.5 h-3.5" /> Logout
        </Link>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6">{children}</main>
    </div>
  );
}
