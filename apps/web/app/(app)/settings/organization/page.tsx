"use client";

export default function OrganizationSettingsPage() {
  return (
    <div className="space-y-4 text-xs">
      <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
        Organization Settings
      </h2>
      <p className="text-slate-500">Manage organization name, slug, and general settings.</p>

      <div className="space-y-3 max-w-md pt-2">
        <div>
          <label className="block font-medium text-slate-400 mb-1">Organization Name</label>
          <input
            type="text"
            defaultValue="Axorks Dev House"
            className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 rounded focus:outline-none focus:border-violet-500"
          />
        </div>
      </div>
    </div>
  );
}
