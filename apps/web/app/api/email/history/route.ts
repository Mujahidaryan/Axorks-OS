import { NextRequest, NextResponse } from "next/server";

// Global in-memory storage for EmailHistory records
const EMAIL_HISTORY_STORE: any[] = [
  {
    id: "msg_init_01",
    messageId: "res_9a8f7d6e5c4b",
    recipient: "alex.tech@acmecorp.com",
    to: ["alex.tech@acmecorp.com"],
    cc: [],
    bcc: [],
    subject: "Project Proposal & Scope of Work for Acme Corp",
    html: "<p>Dear Alex, please find our proposal attached.</p>",
    status: "Sent",
    createdAt: new Date(Date.now() - 3600000 * 2).toISOString(),
    sentBy: "Sarah Jenkins (Axorks Solutions)",
    attachmentsCount: 1,
    provider: "Resend",
    deliveryStatus: "Delivered",
    error: null,
  },
  {
    id: "msg_init_02",
    messageId: "res_1a2b3c4d5e6f",
    recipient: "contact@innovate.io",
    to: ["contact@innovate.io"],
    cc: ["team@axorks.com"],
    bcc: [],
    subject: "Meeting Invitation: Axorks & Innovate Tech",
    html: "<p>Hi Team, looking forward to our discovery call.</p>",
    status: "Sent",
    createdAt: new Date(Date.now() - 3600000 * 24).toISOString(),
    sentBy: "System User",
    attachmentsCount: 0,
    provider: "Resend",
    deliveryStatus: "Delivered",
    error: null,
  },
  {
    id: "msg_init_03",
    messageId: "res_778899aabbcc",
    recipient: "finance@globaltech.org",
    to: ["finance@globaltech.org"],
    cc: [],
    bcc: [],
    subject: "Invoice #INV-2026-004 from Axorks Inc.",
    html: "<p>Please find attached Invoice #INV-2026-004.</p>",
    status: "Sent",
    createdAt: new Date(Date.now() - 3600000 * 48).toISOString(),
    sentBy: "Billing Dept",
    attachmentsCount: 1,
    provider: "Resend",
    deliveryStatus: "Delivered",
    error: null,
  }
];

export function addEmailToHistory(record: any) {
  EMAIL_HISTORY_STORE.unshift(record);
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const search = searchParams.get("search")?.toLowerCase() || "";
  const statusFilter = searchParams.get("status") || "";

  let filtered = [...EMAIL_HISTORY_STORE];

  if (search) {
    filtered = filtered.filter(
      (item) =>
        item.recipient.toLowerCase().includes(search) ||
        item.subject.toLowerCase().includes(search) ||
        item.sentBy.toLowerCase().includes(search)
    );
  }

  if (statusFilter) {
    filtered = filtered.filter((item) => item.status.toLowerCase() === statusFilter.toLowerCase());
  }

  // Calculate Email Analytics
  const now = new Date();
  const todayStr = now.toISOString().split("T")[0];

  const sentToday = EMAIL_HISTORY_STORE.filter((e) => e.createdAt.startsWith(todayStr)).length;
  const totalSent = EMAIL_HISTORY_STORE.filter((e) => e.status === "Sent").length;
  const totalFailed = EMAIL_HISTORY_STORE.filter((e) => e.status === "Failed").length;

  const analytics = {
    sentToday,
    thisWeek: EMAIL_HISTORY_STORE.length,
    thisMonth: EMAIL_HISTORY_STORE.length,
    bounceRate: "0.0%",
    failedEmails: totalFailed,
    totalSent,
    topContacts: [
      { email: "alex.tech@acmecorp.com", count: 4 },
      { email: "contact@innovate.io", count: 3 },
      { email: "finance@globaltech.org", count: 2 },
    ]
  };

  return NextResponse.json({
    success: true,
    data: filtered,
    analytics,
  });
}
