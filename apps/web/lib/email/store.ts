// In-memory email history store shared across API routes.
// In production this would be backed by the database via FastAPI.

export const EMAIL_HISTORY_STORE: any[] = [
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
  },
];

export function addEmailToHistory(record: any) {
  EMAIL_HISTORY_STORE.unshift(record);
}
