"use client";

import { use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { CRMOnePageView } from "@/components/crm/crm-one-page-view";
import { InlineEditableField } from "@/components/crm/inline-editable-field";
import Link from "next/link";

export default function ContactDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const queryClient = useQueryClient();

  const { data: contact, isLoading } = useQuery({
    queryKey: ["contact", id],
    queryFn: () => apiClient(`/api/v1/contacts/${id}`).then((r: any) => r.data),
    enabled: !!id,
  });

  const updateField = useMutation({
    mutationFn: (updates: Record<string, any>) =>
      apiClient(`/api/v1/contacts/${id}`, {
        method: "PATCH",
        body: JSON.stringify(updates),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contact", id] });
      toast.success("Updated");
    },
  });

  if (isLoading || !contact) {
    return <div className="flex items-center justify-center h-full text-slate-500 text-sm">Loading contact...</div>;
  }

  const fullName = [contact.first_name, contact.last_name].filter(Boolean).join(" ") || "Unnamed";

  const sections = [
    {
      id: "details",
      title: "Contact Info",
      content: (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <InlineEditableField label="First Name" value={contact.first_name} onSave={(v) => updateField.mutate({ first_name: v })} />
          <InlineEditableField label="Last Name" value={contact.last_name} onSave={(v) => updateField.mutate({ last_name: v })} />
          <InlineEditableField label="Email" value={contact.email} onSave={(v) => updateField.mutate({ email: v })} />
          <InlineEditableField label="Phone" value={contact.phone} onSave={(v) => updateField.mutate({ phone: v })} />
          <InlineEditableField label="Title" value={contact.title} onSave={(v) => updateField.mutate({ title: v })} />
          <InlineEditableField label="LinkedIn" value={contact.linkedin_url} onSave={(v) => updateField.mutate({ linkedin_url: v })} />
        </div>
      ),
    },
    {
      id: "company",
      title: "Company",
      content: contact.company_id ? (
        <Link href={`/crm/companies/${contact.company_id}`} className="text-xs text-violet-400 hover:underline">
          View company →
        </Link>
      ) : (
        <p className="text-xs text-slate-500">No company linked</p>
      ),
    },
  ];

  return (
    <CRMOnePageView
      entityType="contact"
      entityId={id}
      name={fullName}
      status={contact.title || undefined}
      statusColor="bg-cyan-500/20 text-cyan-400"
      sections={sections}
    />
  );
}
