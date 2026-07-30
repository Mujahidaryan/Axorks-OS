"use client";

import { ReactNode, useRef, useState } from "react";
import { TimelineFeed } from "./timeline-feed";
import { NotesPanel } from "./notes-panel";
import { CallsPanel } from "./calls-panel";
import { QuickActions } from "./quick-actions";
import { AISalesPanel } from "@/components/ai/ai-sales-panel";
import {
  Building2, Mail, Phone, Globe, MapPin, Tag,
  ChevronDown, Sparkles,
} from "lucide-react";

interface Section {
  id: string;
  title: string;
  icon?: ReactNode;
  content: ReactNode;
  /** If true the section starts collapsed */
  defaultClosed?: boolean;
}

interface CRMOnePageViewProps {
  /** Type of entity: "company" | "contact" | "deal" | "lead" */
  entityType: string;
  entityId: string;
  /** Entity display name */
  name: string;
  /** Status badge */
  status?: string;
  statusColor?: string;
  /** Header actions (edit, delete, convert, etc) */
  headerActions?: ReactNode;
  /** All One-Page sections – rendered in order */
  sections: Section[];
}

function SectionBlock({ title, icon, content, defaultClosed }: Section) {
  const detailsRef = useRef<HTMLDetailsElement>(null);

  return (
    <details ref={detailsRef} open={!defaultClosed} className="group border border-slate-800 rounded-xl overflow-hidden">
      <summary className="flex items-center gap-2 px-4 py-3 cursor-pointer select-none hover:bg-slate-900/60 transition">
        <ChevronDown className="w-3.5 h-3.5 text-slate-500 transition-transform group-open:rotate-0 -rotate-90" />
        {icon && <span className="text-slate-500">{icon}</span>}
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">{title}</span>
      </summary>
      <div className="px-4 pb-4 pt-1">{content}</div>
    </details>
  );
}

export function CRMOnePageView({
  entityType,
  entityId,
  name,
  status,
  statusColor = "bg-emerald-500/20 text-emerald-400",
  headerActions,
  sections,
}: CRMOnePageViewProps) {
  const notesRef = useRef<HTMLDivElement>(null);
  const callsRef = useRef<HTMLDivElement>(null);
  const [showAIPanel, setShowAIPanel] = useState(true);

  const scrollTo = (ref: React.RefObject<HTMLDivElement | null>) => {
    ref.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60 backdrop-blur-sm sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-700 flex items-center justify-center text-white font-bold text-sm">
            {name?.[0]?.toUpperCase() || "?"}
          </div>
          <div>
            <h1 className="text-lg font-bold text-white leading-tight">{name}</h1>
            {status && (
              <span className={`inline-block mt-0.5 px-2 py-0.5 rounded-full text-[10px] font-semibold ${statusColor}`}>
                {status}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {headerActions}
          <button
            onClick={() => setShowAIPanel(!showAIPanel)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
              showAIPanel
                ? "bg-violet-600/20 border-violet-500/50 text-violet-300"
                : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-violet-400" />
            AI Copilot
          </button>
        </div>
      </div>

      {/* Body: Main + Timeline + AI Panel */}
      <div className="flex-1 flex overflow-hidden">
        {/* Main scrollable content */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
          {sections.map((s) => (
            <SectionBlock key={s.id} {...s} />
          ))}

          {/* Notes section */}
          <div ref={notesRef}>
            <SectionBlock
              id="notes"
              title="Notes"
              content={<NotesPanel entityType={entityType} entityId={entityId} />}
            />
          </div>

          {/* Calls section */}
          <div ref={callsRef}>
            <SectionBlock
              id="calls"
              title="Calls"
              content={<CallsPanel entityType={entityType} entityId={entityId} />}
            />
          </div>
        </div>

        {/* Timeline sidebar */}
        <div className="w-64 border-l border-slate-800 bg-slate-950/40 flex flex-col shrink-0">
          <div className="px-4 py-3 border-b border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Timeline</span>
          </div>
          <div className="flex-1 overflow-y-auto px-3 py-3">
            <TimelineFeed entityType={entityType} entityId={entityId} />
          </div>
        </div>

        {/* AI Sales Copilot Panel */}
        {showAIPanel && <AISalesPanel entityType={entityType} entityId={entityId} />}
      </div>

      {/* Floating Quick Actions */}
      <QuickActions
        onAddNote={() => scrollTo(notesRef)}
        onLogCall={() => scrollTo(callsRef)}
      />
    </div>
  );
}
