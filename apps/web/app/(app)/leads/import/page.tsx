"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import Link from "next/link";
import { ArrowLeft, Upload, Check, FileText } from "lucide-react";

const LEAD_FIELDS = [
  { id: "business_name", label: "Business Name" },
  { id: "decision_maker_name", label: "Decision Maker Name" },
  { id: "decision_maker_title", label: "Decision Maker Title" },
  { id: "email", label: "Email Address" },
  { id: "phone", label: "Phone Number" },
  { id: "website", label: "Website URL" },
  { id: "industry", label: "Industry" },
  { id: "country", label: "Country" },
  { id: "company_size", label: "Company Size" },
  { id: "source", label: "Source" },
  { id: "status", label: "Status" },
];

export function CSVImportPage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [filename, setFilename] = useState("");
  const [csvHeaders, setCsvHeaders] = useState<string[]>([]);
  const [csvRows, setCsvRows] = useState<dict<string, string>[]>([]);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFilename(file.name);
    const reader = new FileReader();

    reader.onload = (evt) => {
      const text = evt.target?.result as string;
      const lines = text.split("\n").filter((l) => l.trim());
      if (lines.length === 0) return;

      const headers = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""));
      setCsvHeaders(headers);

      const parsedRows: any[] = [];
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(",").map((v) => v.trim().replace(/^"|"$/g, ""));
        const row: Record<string, string> = {};
        headers.forEach((h, idx) => {
          row[h] = values[idx] || "";
        });
        parsedRows.push(row);
      }

      setCsvRows(parsedRows);

      // Auto-guess mapping
      const initialMap: Record<string, string> = {};
      headers.forEach((h) => {
        const match = LEAD_FIELDS.find(
          (f) => f.id.toLowerCase() === h.toLowerCase().replace(/\s+/g, "_") || f.label.toLowerCase() === h.toLowerCase()
        );
        if (match) {
          initialMap[h] = match.id;
        }
      });
      setMapping(initialMap);
      setStep(2);
    };

    reader.readAsText(file);
  };

  const handleImport = async () => {
    setLoading(true);
    try {
      const res = await apiClient("/api/v1/leads/import", {
        method: "POST",
        body: JSON.stringify({
          filename,
          column_mapping: mapping,
          csv_rows: csvRows,
        }),
      });
      setImportResult(res);
      setStep(3);
      toast.success("CSV Import completed!");
    } catch (err: any) {
      toast.error(err.message || "Failed to import CSV");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <Link href="/leads" className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-100">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to leads
        </Link>
        <h1 className="text-xl font-bold tracking-tight mt-2">CSV Lead Import Wizard</h1>
        <p className="text-slate-500 text-xs mt-1">Import up to 10,000 leads with dynamic column mapping</p>
      </div>

      {step === 1 && (
        <div className="glass p-12 rounded-2xl border border-dashed border-slate-700 text-center space-y-4">
          <Upload className="w-10 h-10 mx-auto text-violet-400" />
          <h2 className="text-sm font-semibold">Upload CSV File</h2>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Select a CSV file containing your leads data. Headers will be mapped automatically where possible.
          </p>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            className="hidden"
            id="csv-file-input"
          />
          <label
            htmlFor="csv-file-input"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs cursor-pointer shadow-lg shadow-violet-600/20 transition"
          >
            Choose File
          </label>
        </div>
      )}

      {step === 2 && (
        <div className="glass p-6 rounded-2xl border border-slate-800 space-y-6">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-sm font-semibold">Map Columns ({csvRows.length} rows found)</h2>
              <p className="text-xs text-slate-400">{filename}</p>
            </div>
            <button
              onClick={handleImport}
              disabled={loading}
              className="px-4 py-2 rounded bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs disabled:opacity-50"
            >
              {loading ? "Importing..." : "Start Import"}
            </button>
          </div>

          <div className="space-y-3">
            {csvHeaders.map((header) => (
              <div key={header} className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
                <span className="font-mono text-slate-300">{header}</span>
                <span className="text-slate-500">→</span>
                <select
                  value={mapping[header] || ""}
                  onChange={(e) => setMapping({ ...mapping, [header]: e.target.value })}
                  className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded focus:outline-none text-slate-200 text-xs"
                >
                  <option value="">-- Skip Column --</option>
                  {LEAD_FIELDS.map((f) => (
                    <option key={f.id} value={f.id}>{f.label}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </div>
      )}

      {step === 3 && importResult && (
        <div className="glass p-8 rounded-2xl border border-slate-800 text-center space-y-4">
          <Check className="w-12 h-12 mx-auto text-emerald-400 bg-emerald-500/10 p-2 rounded-full border border-emerald-500/30" />
          <h2 className="text-lg font-bold">Import Completed!</h2>
          <div className="flex justify-center gap-6 text-xs pt-2">
            <div>
              <span className="text-slate-400 block">Successfully Imported</span>
              <span className="text-xl font-bold text-emerald-400">{importResult.imported_rows}</span>
            </div>
            <div>
              <span className="text-slate-400 block">Failed Rows</span>
              <span className="text-xl font-bold text-rose-400">{importResult.failed_rows}</span>
            </div>
          </div>
          <div className="pt-4">
            <button
              onClick={() => router.push("/leads")}
              className="px-6 py-2 rounded bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs"
            >
              View Leads
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default CSVImportPage;
