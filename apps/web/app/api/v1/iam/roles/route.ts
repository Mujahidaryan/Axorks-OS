import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const MOCK_ROLES = [
  { id: "r_01", name: "Founder", description: "Full supreme unrestricted access across all modules", is_custom: false, grant_percentage: 100, permissions: ["*"] },
  { id: "r_02", name: "Co-Founder", description: "Near-founder organizational access", is_custom: false, grant_percentage: 95, permissions: ["crm:*", "sales:*", "projects:*", "finance:*", "hr:*", "users:*"] },
  { id: "r_03", name: "CEO", description: "Executive organizational lead", is_custom: false, grant_percentage: 95, permissions: ["crm:*", "sales:*", "projects:*", "finance:*", "hr:*"] },
  { id: "r_04", name: "CTO", description: "Engineering & architecture lead", is_custom: false, grant_percentage: 90, permissions: ["dev:*", "projects:*", "knowledge:*", "integrations:*"] },
  { id: "r_05", name: "Project Manager", description: "Project delivery & Kanban board management", is_custom: false, grant_percentage: 80, permissions: ["projects:*", "crm:read", "tasks:*"] },
  { id: "r_06", name: "HR Manager", description: "Human resources, hiring & employee profiles", is_custom: false, grant_percentage: 85, permissions: ["hr:*", "recruitment:*", "users:read"] },
  { id: "r_07", name: "Accounts Manager", description: "Financial ledgers, invoices & payroll", is_custom: false, grant_percentage: 85, permissions: ["finance:*", "invoices:*", "payments:*"] },
  { id: "r_08", name: "Sales Manager", description: "Lead pipeline & client proposals", is_custom: false, grant_percentage: 80, permissions: ["leads:*", "crm:*", "proposals:*"] },
  { id: "r_09", name: "Software Engineer", description: "Standard engineering & dev hub access", is_custom: false, grant_percentage: 70, permissions: ["dev:read", "dev:write", "projects:read", "knowledge:read"] },
];

export async function GET(req: NextRequest) {
  try {
    const authHeader = req.headers.get("authorization");
    const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/roles`, {
      headers: { ...(authHeader ? { Authorization: authHeader } : {}) },
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    // Fallback
  }

  return NextResponse.json({ data: MOCK_ROLES });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    try {
      const authHeader = req.headers.get("authorization");
      const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/roles`, {
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

    const newRole = {
      id: `r_${Date.now()}`,
      name: body.name,
      description: body.description || "Custom enterprise role",
      is_custom: true,
      grant_percentage: body.grant_percentage || 100,
      permissions: body.permissions || [],
    };

    MOCK_ROLES.push(newRole);
    return NextResponse.json({ data: newRole });
  } catch (error: any) {
    return NextResponse.json(
      { errors: [{ message: error.message || "Failed to create role" }] },
      { status: 500 }
    );
  }
}
