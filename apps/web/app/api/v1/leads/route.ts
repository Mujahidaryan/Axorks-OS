import { NextRequest, NextResponse } from "next/server";
import { LEADS_STORE, addLeadToStore } from "@/lib/leads-store";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const search = searchParams.get("search")?.toLowerCase() || "";
  const statusFilter = searchParams.get("status") || "";

  try {
    // Attempt to proxy to FastAPI backend
    const authHeader = req.headers.get("authorization");
    const backendRes = await fetch(`${API_BASE_URL}/api/v1/leads?${searchParams.toString()}`, {
      headers: {
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    // FastAPI backend unreachable - fallback to LEADS_STORE
  }

  // Fallback to LEADS_STORE
  let filtered = [...LEADS_STORE];

  if (search) {
    filtered = filtered.filter(
      (l) =>
        (l.business_name && l.business_name.toLowerCase().includes(search)) ||
        (l.decision_maker_name && l.decision_maker_name.toLowerCase().includes(search)) ||
        (l.email && l.email.toLowerCase().includes(search)) ||
        (l.phone && l.phone.toLowerCase().includes(search))
    );
  }

  if (statusFilter) {
    filtered = filtered.filter((l) => l.status.toLowerCase() === statusFilter.toLowerCase());
  }

  return NextResponse.json({
    data: filtered,
    meta: {
      page: 1,
      per_page: 100,
      total: filtered.length,
      total_pages: 1,
    },
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    // Attempt to forward to FastAPI backend
    try {
      const authHeader = req.headers.get("authorization");
      const backendRes = await fetch(`${API_BASE_URL}/api/v1/leads`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(authHeader ? { Authorization: authHeader } : {}),
        },
        body: JSON.stringify(body),
      });

      if (backendRes.ok) {
        const data = await backendRes.json();
        return NextResponse.json(data);
      }
    } catch (err) {
      // FastAPI backend unreachable - fallback to LEADS_STORE
    }

    // Process fallback lead creation (ALL fields optional for businesses created from scratch)
    const newLead = addLeadToStore(body);

    return NextResponse.json({
      data: newLead,
      message: "Lead created successfully",
    });
  } catch (error: any) {
    return NextResponse.json(
      {
        errors: [{ message: error.message || "Failed to create lead" }],
      },
      { status: 500 }
    );
  }
}
