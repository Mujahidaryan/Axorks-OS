import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(req: NextRequest) {
  try {
    const authHeader = req.headers.get("authorization");
    const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/dashboard`, {
      headers: { ...(authHeader ? { Authorization: authHeader } : {}) },
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    // Fallback
  }

  return NextResponse.json({
    data: {
      total_employees: 14,
      online_employees: 9,
      offline_employees: 3,
      locked_accounts: 0,
      suspended_accounts: 1,
      pending_invitations: 1,
      todays_logins: 11,
      failed_attempts: 0,
      recent_audit_logs: [
        {
          id: "log_01",
          actor_email: "founder@axorks.com",
          action: "USER_CREATED",
          entity_type: "user",
          created_at: new Date().toISOString(),
        },
        {
          id: "log_02",
          actor_email: "founder@axorks.com",
          action: "ROLE_UPDATED",
          entity_type: "role",
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
      ],
      latest_joined: [
        {
          id: "u_01",
          first_name: "Sarah",
          last_name: "Connor",
          email: "sarah.c@axorks.com",
          role: "Senior AI Engineer",
          status: "active",
        },
        {
          id: "u_02",
          first_name: "Alex",
          last_name: "Dev",
          email: "alex.d@axorks.com",
          role: "Lead Full Stack Developer",
          status: "active",
        },
      ],
      recent_recordings: [
        {
          id: "rec_01",
          title: "Client Discovery & Technical Review",
          type: "screen",
          duration: 145,
          created_at: new Date().toISOString(),
        },
      ],
    },
  });
}
