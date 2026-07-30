"use client";

import { useState } from "react";
import { Paperclip, X, FileText, Image as ImageIcon, Archive, AlertCircle } from "lucide-react";
import { AttachmentInput } from "@/lib/validators/email";
import { toast } from "sonner";

interface AttachmentUploaderProps {
  attachments: AttachmentInput[];
  onChange: (attachments: AttachmentInput[]) => void;
}

const ALLOWED_EXTENSIONS = ["pdf", "docx", "png", "jpg", "jpeg", "zip"];
const MAX_SIZE_BYTES = 25 * 1024 * 1024; // 25 MB

export function AttachmentUploader({ attachments, onChange }: AttachmentUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (files: FileList | File[]) => {
    const newAttachments: AttachmentInput[] = [];

    Array.from(files).forEach((file) => {
      const ext = file.name.split(".").pop()?.toLowerCase() || "";

      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        toast.error(`File "${file.name}" type not allowed. Supported: PDF, DOCX, PNG, JPG, ZIP.`);
        return;
      }

      if (file.size > MAX_SIZE_BYTES) {
        toast.error(`File "${file.name}" exceeds maximum allowed size of 25 MB.`);
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        newAttachments.push({
          filename: file.name,
          content,
          contentType: file.type,
          size: file.size,
        });

        if (newAttachments.length > 0) {
          onChange([...attachments, ...newAttachments]);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const removeAttachment = (index: number) => {
    onChange(attachments.filter((_, i) => i !== index));
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split(".").pop()?.toLowerCase() || "";
    if (["png", "jpg", "jpeg"].includes(ext)) return <ImageIcon className="w-4 h-4 text-emerald-500" />;
    if (ext === "zip") return <Archive className="w-4 h-4 text-amber-500" />;
    return <FileText className="w-4 h-4 text-blue-500" />;
  };

  const formatSize = (bytes?: number) => {
    if (!bytes) return "";
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
          <Paperclip className="w-3.5 h-3.5" /> Attachments (Max 25MB)
        </label>
        <span className="text-[11px] text-slate-400">PDF, DOCX, PNG, JPG, ZIP</span>
      </div>

      {/* Drag & Drop Area */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files) handleFiles(e.dataTransfer.files);
        }}
        className={`border-2 border-dashed rounded-lg p-3 text-center transition flex flex-col items-center justify-center gap-1.5 cursor-pointer ${
          isDragging
            ? "border-violet-500 bg-violet-50/50 dark:bg-violet-950/20"
            : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50"
        }`}
        onClick={() => {
          const input = document.createElement("input");
          input.type = "file";
          input.multiple = true;
          input.accept = ".pdf,.docx,.png,.jpg,.jpeg,.zip";
          input.onchange = (e: any) => {
            if (e.target.files) handleFiles(e.target.files);
          };
          input.click();
        }}
      >
        <Paperclip className="w-5 h-5 text-slate-400" />
        <p className="text-xs text-slate-600 dark:text-slate-300">
          <span className="font-medium text-violet-600 dark:text-violet-400">Click to upload</span> or drag and drop files here
        </p>
      </div>

      {/* Attachment List */}
      {attachments.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
          {attachments.map((att, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-2 rounded-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs"
            >
              <div className="flex items-center gap-2 truncate">
                {getFileIcon(att.filename)}
                <span className="font-medium text-slate-800 dark:text-slate-200 truncate">{att.filename}</span>
                <span className="text-[10px] text-slate-400">({formatSize(att.size)})</span>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeAttachment(idx);
                }}
                className="text-slate-400 hover:text-red-500 transition p-1"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
