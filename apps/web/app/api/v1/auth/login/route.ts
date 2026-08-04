import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const FOUNDER_USERNAME = process.env.FOUNDER_USERNAME || "muhammad.mujahid";
const FOUNDER_EMAIL = process.env.FOUNDER_EMAIL || "mujahidaryan222149@gmail.com";
const FOUNDER_PASSWORD = process.env.FOUNDER_PASSWORD || "Princearyan1#@#@";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const identifier = (body.identifier || body.email || body.username || "").trim().toLowerCase();
    const password = body.password || "";

    // 1. Try FastAPI backend first
    try {
      const backendRes = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: identifier, password }),
      });

      if (backendRes.ok) {
        const data = await backendRes.json();
        return NextResponse.json(data);
      }
    } catch (err) {
      // Backend not running, use fallback auth handler
    }

    // 2. Founder check (matches Username OR Email + Password)
    const isFounderMatch =
      (identifier === FOUNDER_USERNAME.toLowerCase() || identifier === FOUNDER_EMAIL.toLowerCase()) &&
      password === FOUNDER_PASSWORD;

    if (isFounderMatch) {
      const mockToken = `jwt_founder_session_${Date.now()}`;
      return NextResponse.json({
        data: {
          access_token: mockToken,
          token_type: "bearer",
          user: {
            id: "user_founder_01",
            username: FOUNDER_USERNAME,
            email: FOUNDER_EMAIL,
            first_name: "Muhammad",
            last_name: "Mujahid",
            role: "Founder",
            department: "Management",
          },
        },
      });
    }

    // 3. Employee check from mock/local store
    if (identifier === "sarah" || identifier === "sarah@axorks.com") {
      return NextResponse.json({
        data: {
          access_token: `jwt_employee_session_${Date.now()}`,
          token_type: "bearer",
          user: {
            id: "user_emp_02",
            username: "sarah",
            email: "sarah@axorks.com",
            first_name: "Sarah",
            last_name: "Connor",
            role: "Co-Founder",
            department: "AI Department",
          },
        },
      });
    }

    // 4. Invalid credentials
    return NextResponse.json(
      { errors: [{ message: "Invalid username/email or password" }] },
      { status: 401 }
    );
  } catch (error: any) {
    return NextResponse.json(
      { errors: [{ message: error.message || "Login failed" }] },
      { status: 500 }
    );
  }
}
