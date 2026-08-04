import { NextRequest, NextResponse } from "next/server";
import { usersStore, registerNewUser, findUserByIdentifier } from "@/lib/user-repository";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const search = searchParams.get("search")?.toLowerCase() || "";
  const statusFilter = searchParams.get("status") || "";

  try {
    const authHeader = req.headers.get("authorization");
    const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/users?${searchParams.toString()}`, {
      headers: { ...(authHeader ? { Authorization: authHeader } : {}) },
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    // Fallback
  }

  let filtered = [...usersStore];
  if (search) {
    filtered = filtered.filter(
      (u) =>
        u.first_name.toLowerCase().includes(search) ||
        u.last_name.toLowerCase().includes(search) ||
        u.username.toLowerCase().includes(search) ||
        u.email.toLowerCase().includes(search) ||
        (u.department && u.department.toLowerCase().includes(search))
    );
  }
  if (statusFilter) {
    filtered = filtered.filter((u) => u.status === statusFilter);
  }

  return NextResponse.json({ data: filtered });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    try {
      const authHeader = req.headers.get("authorization");
      const backendRes = await fetch(`${API_BASE_URL}/api/v1/iam/users`, {
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

    const newUser = registerNewUser({
      first_name: body.first_name || "New",
      last_name: body.last_name || "Employee",
      username: body.username || (body.first_name || "user").toLowerCase(),
      email: body.email,
      password: body.password || "AxorksPass123!",
      department: body.department || "Development",
      designation: body.designation || "Team Member",
      role: body.role || "Software Engineer",
      phone: body.phone,
    });

    return NextResponse.json({ data: newUser });
  } catch (error: any) {
    return NextResponse.json(
      { errors: [{ message: error.message || "Failed to create user" }] },
      { status: 500 }
    );
  }
}
