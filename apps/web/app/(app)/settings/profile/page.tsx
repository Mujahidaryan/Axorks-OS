"use client";

import { useAuth } from "@/hooks/use-auth";

export default function ProfileSettingsPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-4 text-xs">
      <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
        Profile Settings
      </h2>
      <p className="text-slate-500">Manage your profile details and preferences.</p>

      <div className="space-y-3 max-w-md pt-2">
        <div>
          <label className="block font-medium text-slate-400 mb-1">Email</label>
          <input
            type="email"
            disabled
            value={user?.email || ""}
            className="w-full px-3 py-2 bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-800 rounded text-slate-500 cursor-not-allowed"
          />
        </div>

        <div>
          <label className="block font-medium text-slate-400 mb-1">First Name</label>
          <input
            type="text"
            defaultValue={user?.first_name || ""}
            className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 rounded focus:outline-none focus:border-violet-500"
          />
        </div>

        <div>
          <label className="block font-medium text-slate-400 mb-1">Last Name</label>
          <input
            type="text"
            defaultValue={user?.last_name || ""}
            className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 rounded focus:outline-none focus:border-violet-500"
          />
        </div>
      </div>
    </div>
  );
}
