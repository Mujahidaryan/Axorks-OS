import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const MOCK_USERS: any[] = [
  {
    id: "user_founder_01",
    organization_id: "00000000-0000-0000-0000-000000000001",
    email: "founder@axorks.com",
    first_name: "Muhammad",
    last_name: "Mujahid",
    display_name: "Founder & CEO",
    employee_id: "EMP-001",
    phone: "+1 (555) 000-1111",
    cnic: "42101-1234567-1",
    department: "Management",
    designation: "Founder & Chief Executive",
    joining_date: "2024-01-01",
    employment_type: "full_time",
    reporting_manager_id: null,
    role: "Founder",
    status: "active",
    avatar_url: null,
    address: "San Francisco, CA",
    emergency_contact: "+1 (555) 999-0000",
    notes: "Supreme unrestricted organizational control.",
    failed_attempts: 0,
    locked_until: null,
    last_login_at: new Date().toISOString(),
    last_login_ip: "192.168.1.1",
    last_login_browser: "Chrome 125",
    last_login_device: "MacBook Pro",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "user_emp_02",
    organization_id: "00000000-0000-0000-0000-000000000001",
    email: "sarah.c@axorks.com",
    first_name: "Sarah",
    last_name: "Connor",
    display_name: "Sarah C.",
    employee_id: "EMP-002",
    phone: "+1 (555) 222-3333",
    cnic: "42101-7654321-2",
    department: "AI Department",
    designation: "Senior AI Engineer",
    joining_date: "2024-03-15",
    employment_type: "full_time",
    reporting_manager_id: "user_founder_01",
    role: "AI Engineer",
    status: "active",
    avatar_url: null,
    address: "Austin, TX",
    emergency_contact: "+1 (555) 888-1111",
    notes: "Lead architect for Gemini & OpenAI LLM workflows.",
    failed_attempts: 0,
    locked_until: null,
    last_login_at: new Date(Date.now() - 1800000).toISOString(),
    last_login_ip: "10.0.0.45",
    last_login_browser: "Safari",
    last_login_device: "iPhone 15 Pro",
    created_at: new Date(Date.now() - 86400000 * 30).toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "user_emp_03",
    organization_id: "00000000-0000-0000-0000-000000000001",
    email: "alex.d@axorks.com",
    first_name: "Alex",
    last_name: "Dev",
    display_name: "Alex Dev",
    employee_id: "EMP-003",
    phone: "+1 (555) 444-5555",
    cnic: null,
    department: "Development",
    designation: "Lead Full Stack Developer",
    joining_date: "2024-02-01",
    employment_type: "full_time",
    reporting_manager_id: "user_founder_01",
    role: "Full Stack Developer",
    status: "active",
    avatar_url: null,
    address: "New York, NY",
    emergency_contact: "+1 (555) 777-2222",
    notes: "Next.js & FastAPI specialist.",
    failed_attempts: 0,
    locked_until: null,
    last_login_at: new Date(Date.now() - 3600000).toISOString(),
    last_login_ip: "172.16.0.12",
    last_login_browser: "Firefox",
    last_login_device: "Windows Desktop",
    created_at: new Date(Date.now() - 86400000 * 60).toISOString(),
    updated_at: new Date().toISOString(),
  },
];

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

  let filtered = [...MOCK_USERS];
  if (search) {
    filtered = filtered.filter(
      (u) =>
        u.first_name.toLowerCase().includes(search) ||
        u.last_name.toLowerCase().includes(search) ||
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

    const newUser = {
      id: `user_${Date.now()}`,
      organization_id: "00000000-0000-0000-0000-000000000001",
      email: body.email,
      first_name: body.first_name || "New",
      last_name: body.last_name || "Employee",
      display_name: `${body.first_name} ${body.last_name}`,
      employee_id: body.employee_id || `EMP-${Math.floor(Math.random() * 900) + 100}`,
      phone: body.phone || null,
      cnic: body.cnic || null,
      department: body.department || "Development",
      designation: body.designation || "Team Member",
      joining_date: body.joining_date || new Date().toISOString().split("T")[0],
      employment_type: body.employment_type || "full_time",
      reporting_manager_id: body.reporting_manager_id || null,
      role: body.role || "member",
      status: body.status || "active",
      avatar_url: body.avatar_url || null,
      address: body.address || null,
      emergency_contact: body.emergency_contact || null,
      notes: body.notes || null,
      failed_attempts: 0,
      locked_until: null,
      last_login_at: null,
      last_login_ip: null,
      last_login_browser: null,
      last_login_device: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    MOCK_USERS.unshift(newUser);
    return NextResponse.json({ data: newUser });
  } catch (error: any) {
    return NextResponse.json(
      { errors: [{ message: error.message || "Failed to create user" }] },
      { status: 500 }
    );
  }
}
