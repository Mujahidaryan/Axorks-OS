"use client";

export default function ShortcutsSettingsPage() {
  return (
    <div className="space-y-4 text-xs">
      <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
        Keyboard Shortcuts
      </h2>
      <div className="space-y-2 max-w-sm pt-2">
        <div className="flex justify-between items-center p-2 rounded bg-slate-100 dark:bg-slate-900">
          <span>Command Palette</span>
          <kbd className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono text-[10px]">
            ⌘K
          </kbd>
        </div>
        <div className="flex justify-between items-center p-2 rounded bg-slate-100 dark:bg-slate-900">
          <span>Keyboard Shortcuts Help</span>
          <kbd className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 font-mono text-[10px]">
            ⌘/
          </kbd>
        </div>
      </div>
    </div>
  );
}
