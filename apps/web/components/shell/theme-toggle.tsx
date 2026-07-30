"use client";

import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <button
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900 transition"
      title="Toggle Dark/Light Mode"
    >
      <Sun className="w-4 h-4 hidden dark:block text-amber-400" />
      <Moon className="w-4 h-4 block dark:hidden text-slate-700" />
    </button>
  );
}
