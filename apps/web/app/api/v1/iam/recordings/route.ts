import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const MOCK_RECORDINGS = [
  {
    id: "rec_demo_01",
    organization_id: "00000000-0000-0000-0000-000000000001",
    user_id: "user_emp_02",
    recorded_by_id: "user_founder_01",
    recording_type: "screen",
    title: "Client Technical Review & Architecture Session",
    file_url: null,
    duration_seconds: 184,
    metadata_json: { browser: "Chrome 125", resolution: "1920x1080", fps: 30 },
    created_at: new Date().toISOString(),
  },
  {
    id: "rec_demo_02",
    organization_id: "00000000-0000-0000-0000-000000000001",
    user_id: "user_emp_03",
    recorded_by_id: "user_founder_01",
    recording_type: "call",
    title: "Client Discovery & Requirements Call",
    file_url: null,
    duration_seconds: 412,
    metadata_json: { audio_codec: "opus", sample_rate: 48000 },
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
];

export async function GET(req: NextRequest) {
  try {
    const authHeader = req.headers.get("authorization");
    const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/recordings`, {
      headers: { ...(authHeader ? { Authorization: authHeader } : {}) },
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    // Fallback
  }

  return NextResponse.json({ data: MOCK_RECORDINGS });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    try {
      const authHeader = req.headers.get("authorization");
      const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/recordings`, {
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
      // Fallback
    }

    const newRec = {
      id: `rec_${Date.now()}`,
      organization_id: "00000000-0000-0000-0000-000000000001",
      user_id: body.user_id || null,
      recorded_by_id: "user_founder_01",
      recording_type: body.recording_type || "screen",
      title: body.title || "Founder Recording",
      file_url: body.file_url || null,
      duration_seconds: body.duration_seconds || 0,
      metadata_json: body.metadata_json || {},
      created_at: new Date().toISOString(),
    };

    MOCK_RECORDINGS.unshift(newRec);
    return NextResponse.json({ data: newRec });
  } catch (error: any) {
    return NextResponse.json(
      { errors: [{ message: error.message || "Failed to save recording" }] },
      { status: 500 }
    );
  }
}
