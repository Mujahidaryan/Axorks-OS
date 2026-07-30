"use client";

import { use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { CRMOnePageView } from "@/components/crm/crm-one-page-view";
import { InlineEditableField } from "@/components/crm/inline-editable-field";
import Link from "next/link";

export default function DealDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const queryClient = useQueryClient();

  const { data: deal, isLoading } = useQuery({
    queryKey: ["deal", id],
    queryFn: () => apiClient(`/api/v1/deals/${id}`).then((r: any) => r.data),
    enabled: !!id,
  });

  const updateField = useMutation({
    mutationFn: (updates: Record<string, any>) =>
      apiClient(`/api/v1/deals/${id}`, {
        method: "PATCH",
        body: JSON.stringify(updates),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deal", id] });
      toast.success("Updated");
    },
  });

  if (isLoading || !deal) {
    return <div className="flex items-center justify-center h-full text-slate-500 text-sm">Loading deal...</div>;
  }

  const statusColor =
    deal.status === "won" ? "bg-emerald-500/20 text-emerald-400" :
    deal.status === "lost" ? "bg-red-500/20 text-red-400" :
    "bg-violet-500/20 text-violet-400";

  const sections = [
    {
      id: "details",
      title: "Deal Info",
      content: (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <InlineEditableField label="Title" value={deal.title} onSave={(v) => updateField.mutate({ title: v })} />
          <InlineEditableField label="Value" value={deal.value?.toString()} onSave={(v) => updateField.mutate({ value: parseFloat(v) || 0 })} />
          <InlineEditableField label="Currency" value={deal.currency} onSave={(v) => updateField.mutate({ currency: v })} />
          <InlineEditableField label="Stage" value={deal.stage} onSave={(v) => updateField.mutate({ stage: v })} />
          <InlineEditableField label="Probability (%)" value={deal.probability?.toString()} onSave={(v) => updateField.mutate({ probability: parseInt(v) || 0 })} />
          <InlineEditableField label="Expected Close" value={deal.expected_close} onSave={(v) => updateField.mutate({ expected_close: v })} />
        </div>
      ),
    },
    {
      id: "company",
      title: "Company",
      content: deal.company_id ? (
        <Link href={`/crm/companies/${deal.company_id}`} className="text-xs text-violet-400 hover:underline">View company →</Link>
      ) : (
        <p className="text-xs text-slate-500">No company linked</p>
      ),
    },
    {
      id: "contact",
      title: "Contact",
      content: deal.contact_id ? (
        <Link href={`/crm/contacts/${deal.contact_id}`} className="text-xs text-violet-400 hover:underline">View contact →</Link>
      ) : (
        <p className="text-xs text-slate-500">No contact linked</p>
      ),
    },
    {
      id: "actions",
      title: "Deal Actions",
      content: (
        <div className="flex gap-2">
          {deal.status === "open" && (
            <>
              <button
                onClick={() => updateField.mutate({ status: "won" })}
                className="px-4 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-medium hover:bg-emerald-500 transition"
              >
                Mark as Won
              </button>
              <button
                onClick={() => updateField.mutate({ status: "lost" })}
                className="px-4 py-1.5 rounded-lg bg-red-600/80 text-white text-xs font-medium hover:bg-red-600 transition"
              >
                Mark as Lost
              </button>
            </>
          )}
          {deal.status !== "open" && (
            <button
              onClick={() => updateField.mutate({ status: "open" })}
              className="px-4 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700 transition"
            >
              Reopen Deal
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <CRMOnePageView
      entityType="deal"
      entityId={id}
      name={deal.title}
      status={deal.status}
      statusColor={statusColor}
      headerActions={
        <span className="text-sm font-bold text-white">
          {deal.value ? `${deal.currency} ${Number(deal.value).toLocaleString()}` : ""}
        </span>
      }
      sections={sections}
    />
  );
}
