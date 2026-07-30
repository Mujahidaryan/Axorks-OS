"use client";

import { use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { CRMOnePageView } from "@/components/crm/crm-one-page-view";
import { InlineEditableField } from "@/components/crm/inline-editable-field";
import { Globe, MapPin, Users, Briefcase, DollarSign, Linkedin, Building2 } from "lucide-react";
import Link from "next/link";

export default function CompanyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const queryClient = useQueryClient();

  const { data: company, isLoading } = useQuery({
    queryKey: ["company", id],
    queryFn: () => apiClient(`/api/v1/companies/${id}`).then((r: any) => r.data),
    enabled: !!id,
  });

  const { data: contacts = [] } = useQuery({
    queryKey: ["contacts", "company", id],
    queryFn: () => apiClient(`/api/v1/contacts?company_id=${id}`).then((r: any) => r.data),
    enabled: !!id,
  });

  const { data: deals = [] } = useQuery({
    queryKey: ["deals", "company", id],
    queryFn: () => apiClient(`/api/v1/deals?company_id=${id}`).then((r: any) => r.data),
    enabled: !!id,
  });

  const updateField = useMutation({
    mutationFn: (updates: Record<string, any>) =>
      apiClient(`/api/v1/companies/${id}`, {
        method: "PATCH",
        body: JSON.stringify(updates),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["company", id] });
      toast.success("Updated");
    },
  });

  if (isLoading || !company) {
    return <div className="flex items-center justify-center h-full text-slate-500 text-sm">Loading company...</div>;
  }

  const sections = [
    {
      id: "details",
      title: "Key Details",
      content: (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <InlineEditableField label="Company Name" value={company.name} onSave={(v) => updateField.mutate({ name: v })} />
          <InlineEditableField label="Industry" value={company.industry} onSave={(v) => updateField.mutate({ industry: v })} />
          <InlineEditableField label="Country" value={company.country} onSave={(v) => updateField.mutate({ country: v })} />
          <InlineEditableField label="Size" value={company.size} onSave={(v) => updateField.mutate({ size: v })} />
          <InlineEditableField label="Revenue Range" value={company.revenue_range} onSave={(v) => updateField.mutate({ revenue_range: v })} />
          <InlineEditableField label="Website" value={company.website} onSave={(v) => updateField.mutate({ website: v })} />
          <InlineEditableField label="LinkedIn" value={company.linkedin_url} onSave={(v) => updateField.mutate({ linkedin_url: v })} />
        </div>
      ),
    },
    {
      id: "contacts",
      title: `Contacts (${contacts.length})`,
      content: (
        <div className="space-y-2">
          {contacts.length === 0 ? (
            <p className="text-xs text-slate-500">No contacts linked yet.</p>
          ) : (
            contacts.map((c: any) => (
              <Link key={c.id} href={`/crm/contacts/${c.id}`} className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-900/40 transition">
                <div className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center text-[10px] font-bold text-violet-400">
                  {c.first_name?.[0]}{c.last_name?.[0]}
                </div>
                <div className="text-xs">
                  <span className="font-medium text-slate-200">{c.first_name} {c.last_name}</span>
                  {c.title && <span className="text-slate-500 ml-2">• {c.title}</span>}
                </div>
                {c.is_primary && <span className="ml-auto px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 text-[10px]">Primary</span>}
              </Link>
            ))
          )}
        </div>
      ),
    },
    {
      id: "deals",
      title: `Deals (${deals.length})`,
      content: (
        <div className="space-y-2">
          {deals.length === 0 ? (
            <p className="text-xs text-slate-500">No deals yet.</p>
          ) : (
            deals.map((d: any) => (
              <Link key={d.id} href={`/crm/deals/${d.id}`} className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-900/40 transition text-xs">
                <span className="font-medium text-slate-200">{d.title}</span>
                <div className="flex items-center gap-3">
                  <span className="text-slate-400">{d.value ? `${d.currency} ${Number(d.value).toLocaleString()}` : "—"}</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                    d.status === "won" ? "bg-emerald-500/10 text-emerald-400" :
                    d.status === "lost" ? "bg-red-500/10 text-red-400" :
                    "bg-violet-500/10 text-violet-400"
                  }`}>{d.status}</span>
                </div>
              </Link>
            ))
          )}
        </div>
      ),
    },
    {
      id: "projects",
      title: "Projects",
      defaultClosed: true,
      content: <p className="text-xs text-slate-500 italic">Coming in Phase 6</p>,
    },
    {
      id: "invoices",
      title: "Invoices",
      defaultClosed: true,
      content: <p className="text-xs text-slate-500 italic">Coming in Phase 9</p>,
    },
  ];

  return (
    <CRMOnePageView
      entityType="company"
      entityId={id}
      name={company.name}
      status={company.industry || undefined}
      statusColor="bg-indigo-500/20 text-indigo-400"
      sections={sections}
    />
  );
}
