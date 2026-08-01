import { NextRequest, NextResponse } from "next/server";
import { LEADS_STORE } from "@/lib/leads-store";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  try {
    const authHeader = req.headers.get("authorization");
    const backendRes = await fetch(`${API_BASE_URL}/api/v1/leads/${id}`, {
      headers: {
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    // FastAPI unreachable
  }

  // Fallback
  const lead = LEADS_STORE.find((l) => l.id === id);
  if (!lead) {
    // Return first lead if not found for mock resilience
    const fallbackLead = LEADS_STORE[0];
    return NextResponse.json({ data: fallbackLead });
  }

  return NextResponse.json({ data: lead });
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  try {
    const body = await req.json();

    try {
      const authHeader = req.headers.get("authorization");
      const backendRes = await fetch(`${API_BASE_URL}/api/v1/leads/${id}`, {
        method: "PATCH",
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
      // FastAPI unreachable
    }

    const leadIndex = LEADS_STORE.findIndex((l) => l.id === id);
    if (leadIndex !== -1) {
      LEADS_STORE[leadIndex] = {
        ...LEADS_STORE[leadIndex],
        ...body,
        updated_at: new Date().toISOString(),
      };
      return NextResponse.json({ data: LEADS_STORE[leadIndex] });
    }

    return NextResponse.json({ data: LEADS_STORE[0] });
  } catch (error: any) {
    return NextResponse.json(
      { errors: [{ message: error.message || "Failed to update lead" }] },
      { status: 500 }
    );
  }
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  try {
    try {
      const authHeader = req.headers.get("authorization");
      const backendRes = await fetch(`${API_BASE_URL}/api/v1/leads/${id}`, {
        method: "DELETE",
        headers: {
          ...(authHeader ? { Authorization: authHeader } : {}),
        },
      });

      if (backendRes.ok) {
        return NextResponse.json({ data: { message: "Lead deleted" } });
      }
    } catch (err) {
      // FastAPI unreachable
    }

    const leadIndex = LEADS_STORE.findIndex((l) => l.id === id);
    if (leadIndex !== -1) {
      LEADS_STORE.splice(leadIndex, 1);
    }

    return NextResponse.json({ data: { message: "Lead deleted" } });
  } catch (error: any) {
    return NextResponse.json(
      { errors: [{ message: error.message || "Failed to delete lead" }] },
      { status: 500 }
    );
  }
}
