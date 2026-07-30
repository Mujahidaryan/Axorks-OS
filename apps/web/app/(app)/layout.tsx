"use client";

import { Sidebar } from "@/components/shell/sidebar";
import { Topbar } from "@/components/shell/topbar";
import { CommandPalette } from "@/components/shell/command-palette";
import { NotificationsPanel } from "@/components/shell/notifications-panel";
import { KeyboardShortcuts } from "@/components/shell/keyboard-shortcuts";
import { PWARegister } from "@/components/shell/pwa-register";
import { MobileNav } from "@/components/shell/mobile-nav";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Topbar />

        <main className="flex-1 p-4 md:p-6 relative pb-20 md:pb-6">
          <NotificationsPanel />
          {children}
        </main>
      </div>

      <CommandPalette />
      <KeyboardShortcuts />
      <MobileNav />
      <PWARegister />
    </div>
  );
}
