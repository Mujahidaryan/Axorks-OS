"use client";

import { use, useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Save, ArrowLeft, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";

export default function KnowledgePageDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const router = useRouter();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const { data: page, isLoading } = useQuery({
    queryKey: ["knowledge-page", slug],
    queryFn: () => apiClient(`/api/v1/knowledge/pages/by-slug/${slug}`).then((r: any) => r.data),
    enabled: !!slug,
  });

  useEffect(() => {
    if (page) {
      setTitle(page.title);
      setContent(page.content || "");
    }
  }, [page]);

  const savePage = useMutation({
    mutationFn: () =>
      apiClient(`/api/v1/knowledge/pages/${page.id}`, {
        method: "PATCH",
        body: JSON.stringify({ title, content }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-page", slug] });
      queryClient.invalidateQueries({ queryKey: ["knowledge-pages"] });
      toast.success("Page saved!");
    },
  });

  const deletePage = useMutation({
    mutationFn: () => apiClient(`/api/v1/knowledge/pages/${page.id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-pages"] });
      toast.success("Page deleted");
      router.push("/knowledge");
    },
  });

  if (isLoading || !page) {
    return <div className="flex items-center justify-center h-full text-slate-500 text-sm">Loading page...</div>;
  }

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <button onClick={() => router.push("/knowledge")} className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Knowledge Base
        </button>
        <div className="flex gap-2">
          <button onClick={() => deletePage.mutate()} className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-red-600/10 text-red-400 text-xs hover:bg-red-600/20 transition">
            <Trash2 className="w-3 h-3" /> Delete
          </button>
          <button onClick={() => savePage.mutate()} className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-violet-600 text-white text-xs font-medium hover:bg-violet-500 transition">
            <Save className="w-3.5 h-3.5" /> Save
          </button>
        </div>
      </div>

      {/* Page Icon & Title */}
      <div className="flex items-center gap-3 pt-4">
        <span className="text-3xl">{page.icon || "📄"}</span>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="text-2xl font-bold text-white bg-transparent border-none outline-none w-full placeholder:text-slate-600"
          placeholder="Untitled"
        />
      </div>

      {/* Metadata */}
      <div className="flex items-center gap-4 text-[10px] text-slate-500 border-b border-slate-800 pb-3">
        <span>Type: <strong className="text-slate-300 capitalize">{page.page_type}</strong></span>
        <span>Slug: <strong className="text-slate-400 font-mono">/{page.slug}</strong></span>
        <span>Last updated: {new Date(page.updated_at).toLocaleDateString()}</span>
      </div>

      {/* Notion-style Content Editor */}
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Start writing... (Markdown supported)"
        rows={30}
        className="w-full bg-transparent text-slate-300 text-sm leading-relaxed resize-none outline-none placeholder:text-slate-600 font-mono"
      />
    </div>
  );
}
