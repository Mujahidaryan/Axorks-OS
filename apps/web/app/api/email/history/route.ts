import { NextRequest, NextResponse } from "next/server";
import { EMAIL_HISTORY_STORE } from "@/lib/email/store";

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
    filtered = filtered.filter(
      (item) => item.status.toLowerCase() === statusFilter.toLowerCase()
    );
  }

  // Calculate Email Analytics
  const now = new Date();
  const todayStr = now.toISOString().split("T")[0];

  const sentToday = EMAIL_HISTORY_STORE.filter((e) =>
    e.createdAt.startsWith(todayStr)
  ).length;
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
    ],
  };

  return NextResponse.json({
    success: true,
    data: filtered,
    analytics,
  });
}
