import { NextRequest, NextResponse } from "next/server";
import { sessionsStore } from "@/lib/user-repository";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(req: NextRequest) {
  try {
    const authHeader = req.headers.get("authorization");
    const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/sessions`, {
      headers: { ...(authHeader ? { Authorization: authHeader } : {}) },
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    // Fallback
  }

  return NextResponse.json({ data: sessionsStore });
}
