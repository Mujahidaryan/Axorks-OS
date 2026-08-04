import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const MOCK_DEPARTMENTS = [
  { id: "d_01", name: "Management", code: "MGT", description: "Executive & Founder Leadership", employee_count: 2 },
  { id: "d_02", name: "Development", code: "DEV", description: "Full Stack & Core Software Engineering", employee_count: 5 },
  { id: "d_03", name: "AI Department", code: "AI", description: "LLM, RAG & Machine Learning Engineering", employee_count: 3 },
  { id: "d_04", name: "UI/UX", code: "DES", description: "Product Design & Design System", employee_count: 2 },
  { id: "d_05", name: "HR", code: "HR", description: "Human Resources & Talent Acquisition", employee_count: 1 },
  { id: "d_06", name: "Accounts & Finance", code: "ACC", description: "Financial Planning & Payroll", employee_count: 1 },
];

export async function GET(req: NextRequest) {
  try {
    const authHeader = req.headers.get("authorization");
    const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/departments`, {
      headers: { ...(authHeader ? { Authorization: authHeader } : {}) },
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    // Fallback
  }

  return NextResponse.json({ data: MOCK_DEPARTMENTS });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    try {
      const authHeader = req.headers.get("authorization");
      const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/departments`, {
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

    const newDept = {
      id: `d_${Date.now()}`,
      name: body.name,
      code: body.code || body.name.substring(0, 3).toUpperCase(),
      description: body.description || `${body.name} Department`,
      employee_count: 0,
    };

    MOCK_DEPARTMENTS.push(newDept);
    return NextResponse.json({ data: newDept });
  } catch (error: any) {
    return NextResponse.json(
      { errors: [{ message: error.message || "Failed to create department" }] },
      { status: 500 }
    );
  }
}
