"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { MessageSquare, Phone, Mail, Activity, ChevronRight } from "lucide-react";

const ICON_MAP: Record<string, any> = {
  note: MessageSquare,
  call: Phone,
  email: Mail,
  activity: Activity,
};

const COLOR_MAP: Record<string, string> = {
  note: "text-amber-400 bg-amber-500/10",
  call: "text-cyan-400 bg-cyan-500/10",
  email: "text-violet-400 bg-violet-500/10",
  activity: "text-slate-400 bg-slate-500/10",
};

interface TimelineFeedProps {
  entityType: string;
  entityId: string;
}

export function TimelineFeed({ entityType, entityId }: TimelineFeedProps) {
  const { data: events = [], isLoading } = useQuery({
    queryKey: ["timeline", entityType, entityId],
    queryFn: () => apiClient(`/api/v1/${entityType}/${entityId}/timeline`),
    enabled: !!entityId,
  });

  if (isLoading) {
    return <div className="text-xs text-slate-500 py-4">Loading timeline...</div>;
  }

  if (events.length === 0) {
    return <div className="text-xs text-slate-500 py-4">No activity yet</div>;
  }

  return (
    <div className="space-y-1">
      {events.map((event: any) => {
        const Icon = ICON_MAP[event.type] || Activity;
        const colors = COLOR_MAP[event.type] || COLOR_MAP.activity;

        return (
          <div key={event.id} className="flex gap-3 p-2 rounded-lg hover:bg-slate-900/40 transition">
            <div className={`w-6 h-6 rounded-md flex items-center justify-center shrink-0 ${colors}`}>
              <Icon className="w-3 h-3" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-slate-200 truncate">{event.title}</p>
              {event.detail && (
                <p className="text-[10px] text-slate-500 truncate mt-0.5">{event.detail}</p>
              )}
              <p className="text-[10px] text-slate-600 mt-0.5">
                {new Date(event.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
