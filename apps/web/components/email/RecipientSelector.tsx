"use client";

import { useState } from "react";
import { X, Plus, User, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface RecipientSelectorProps {
  label: string;
  value: string[];
  onChange: (emails: string[]) => void;
  placeholder?: string;
}

const SAMPLE_SUGGESTIONS = [
  { name: "Alex Tech", email: "alex.tech@acmecorp.com", company: "Acme Corp" },
  { name: "Sarah Connor", email: "contact@innovate.io", company: "Innovate Tech" },
  { name: "David Miller", email: "finance@globaltech.org", company: "GlobalTech" },
  { name: "Jessica Alba", email: "jessica@apexsolutions.com", company: "Apex Solutions" },
  { name: "Michael Scott", email: "m.scott@dundermifflin.com", company: "Dunder Mifflin" },
];

export function RecipientSelector({
  label,
  value,
  onChange,
  placeholder = "Type email and press Enter...",
}: RecipientSelectorProps) {
  const [input, setInput] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if ((e.key === "Enter" || e.key === ",") && input.trim()) {
      e.preventDefault();
      addEmail(input.trim());
    } else if (e.key === "Backspace" && !input && value.length > 0) {
      removeEmail(value.length - 1);
    }
  };

  const addEmail = (email: string) => {
    const cleaned = email.toLowerCase().trim();
    if (cleaned && !value.includes(cleaned)) {
      onChange([...value, cleaned]);
    }
    setInput("");
    setShowDropdown(false);
  };

  const removeEmail = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const filteredSuggestions = SAMPLE_SUGGESTIONS.filter(
    (item) =>
      !value.includes(item.email) &&
      (item.email.toLowerCase().includes(input.toLowerCase()) ||
        item.name.toLowerCase().includes(input.toLowerCase()) ||
        item.company.toLowerCase().includes(input.toLowerCase()))
  );

  return (
    <div className="relative flex flex-col gap-1.5">
      <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        {label}
      </label>
      <div className="min-h-[42px] w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 py-1.5 flex flex-wrap items-center gap-1.5 focus-within:ring-2 focus-within:ring-violet-500 focus-within:border-transparent transition">
        {value.map((email, idx) => (
          <span
            key={idx}
            className="inline-flex items-center gap-1 bg-violet-50 dark:bg-violet-950/50 text-violet-700 dark:text-violet-300 text-xs px-2.5 py-1 rounded-full border border-violet-200 dark:border-violet-800/50 font-medium"
          >
            {email}
            <button
              type="button"
              onClick={() => removeEmail(idx)}
              className="text-violet-400 hover:text-violet-600 dark:hover:text-violet-200 rounded-full p-0.5"
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}
        <input
          type="text"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setShowDropdown(true);
          }}
          onFocus={() => setShowDropdown(true)}
          onKeyDown={handleKeyDown}
          placeholder={value.length === 0 ? placeholder : ""}
          className="flex-1 bg-transparent border-none text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none min-w-[180px]"
        />
      </div>

      {/* Autocomplete Dropdown */}
      {showDropdown && input.length > 0 && filteredSuggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 z-50 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-xl max-h-48 overflow-y-auto py-1">
          {filteredSuggestions.map((item) => (
            <button
              key={item.email}
              type="button"
              onClick={() => addEmail(item.email)}
              className="w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800 transition"
            >
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-500 font-bold text-[10px]">
                  {item.name[0]}
                </div>
                <div>
                  <div className="font-semibold text-slate-800 dark:text-slate-200">{item.name}</div>
                  <div className="text-slate-400 text-[11px]">{item.email}</div>
                </div>
              </div>
              <span className="text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-500 px-2 py-0.5 rounded">
                {item.company}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
