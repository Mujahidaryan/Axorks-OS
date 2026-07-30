"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Pin, Send } from "lucide-react";

interface NotesPanelProps {
  entityType: string;
  entityId: string;
}

export function NotesPanel({ entityType, entityId }: NotesPanelProps) {
  const queryClient = useQueryClient();
  const [content, setContent] = useState("");

  const { data: notes = [] } = useQuery({
    queryKey: ["notes", entityType, entityId],
    queryFn: () => apiClient(`/api/v1/notes?entity_type=${entityType}&entity_id=${entityId}`),
    enabled: !!entityId,
  });

  const addNote = useMutation({
    mutationFn: () =>
      apiClient("/api/v1/notes", {
        method: "POST",
        body: JSON.stringify({ entity_type: entityType, entity_id: entityId, content }),
      }),
    onSuccess: () => {
      setContent("");
      queryClient.invalidateQueries({ queryKey: ["notes", entityType, entityId] });
      queryClient.invalidateQueries({ queryKey: ["timeline", entityType, entityId] });
      toast.success("Note added");
    },
  });

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Add a note..."
          rows={2}
          className="flex-1 px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs focus:outline-none focus:border-violet-500 resize-none"
        />
        <button
          onClick={() => addNote.mutate()}
          disabled={!content.trim() || addNote.isPending}
          className="self-end px-3 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs disabled:opacity-50"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="space-y-2 max-h-60 overflow-y-auto">
        {notes.map((note: any) => (
          <div key={note.id} className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs space-y-1">
            <div className="flex justify-between items-start">
              <p className="text-slate-200 whitespace-pre-wrap">{note.content}</p>
              {note.is_pinned && <Pin className="w-3 h-3 text-amber-400 shrink-0" />}
            </div>
            <p className="text-[10px] text-slate-600">{new Date(note.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
