import { NextRequest, NextResponse } from "next/server";
import { registerNewUser, recordLoginSession } from "@/lib/user-repository";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    // 1. Attempt FastAPI backend if available
    try {
      const backendRes = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (backendRes.ok) {
        const data = await backendRes.json();
        return NextResponse.json(data);
      }
    } catch (err) {
      // Fallback to local serverless handler
    }

    // 2. Register user in central repository
    const newUser = registerNewUser({
      email: body.email,
      password: body.password,
      username: body.username,
      first_name: body.first_name || "New",
      last_name: body.last_name || "User",
    });

    const session = recordLoginSession(newUser, "127.0.0.1", "Web Browser");
    const mockToken = `jwt_session_${newUser.id}_${Date.now()}`;

    return NextResponse.json({
      data: {
        access_token: mockToken,
        token_type: "bearer",
        user: {
          id: newUser.id,
          username: newUser.username,
          email: newUser.email,
          first_name: newUser.first_name,
          last_name: newUser.last_name,
          role: newUser.role,
          department: newUser.department,
        },
        session,
      },
    });
  } catch (error: any) {
    return NextResponse.json(
      { errors: [{ message: error.message || "Registration failed" }] },
      { status: 500 }
    );
  }
}
