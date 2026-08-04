export interface StoredUser {
  id: string;
  organization_id: string;
  email: string;
  username: string;
  hashed_password?: string;
  password?: string;
  first_name: string;
  last_name: string;
  display_name: string;
  employee_id: string;
  phone?: string | null;
  cnic?: string | null;
  department: string;
  designation: string;
  joining_date: string;
  employment_type: string;
  role: string;
  status: "active" | "inactive" | "suspended" | "locked" | "pending_invitation";
  avatar_url?: string | null;
  last_login_at?: string | null;
  last_login_ip?: string | null;
  last_login_browser?: string | null;
  last_login_device?: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserSession {
  session_id: string;
  user_id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  ip_address: string;
  device: string;
  login_at: string;
  last_active_at: string;
}

const FOUNDER_USERNAME = process.env.FOUNDER_USERNAME || "muhammad.mujahid";
const FOUNDER_EMAIL = process.env.FOUNDER_EMAIL || "mujahidaryan222149@gmail.com";
const FOUNDER_PASSWORD = process.env.FOUNDER_PASSWORD || "Princearyan1#@#@";

// In-memory store persistent across hot reloads in Next.js dev/serverless container
const globalUserStore = globalThis as unknown as {
  __axorks_users?: StoredUser[];
  __axorks_sessions?: UserSession[];
};

if (!globalUserStore.__axorks_users) {
  globalUserStore.__axorks_users = [
    {
      id: "user_founder_01",
      organization_id: "00000000-0000-0000-0000-000000000001",
      email: FOUNDER_EMAIL.toLowerCase(),
      username: FOUNDER_USERNAME.toLowerCase(),
      password: FOUNDER_PASSWORD,
      first_name: "Muhammad",
      last_name: "Mujahid",
      display_name: "Muhammad Mujahid (Founder)",
      employee_id: "EMP-001",
      phone: "+1 (555) 000-1111",
      department: "Management",
      designation: "Founder & Chief Executive",
      joining_date: "2024-01-01",
      employment_type: "full_time",
      role: "Founder",
      status: "active",
      last_login_at: new Date().toISOString(),
      last_login_ip: "192.168.1.1",
      last_login_browser: "Chrome",
      last_login_device: "MacBook Pro",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: "user_emp_02",
      organization_id: "00000000-0000-0000-0000-000000000001",
      email: "sarah@axorks.com",
      username: "sarah",
      password: "AxorksPass123!",
      first_name: "Sarah",
      last_name: "Connor",
      display_name: "Sarah Connor",
      employee_id: "EMP-002",
      phone: "+1 (555) 222-3333",
      department: "AI Department",
      designation: "Senior AI Engineer",
      joining_date: "2024-03-15",
      employment_type: "full_time",
      role: "Co-Founder",
      status: "active",
      last_login_at: new Date(Date.now() - 3600000).toISOString(),
      last_login_ip: "10.0.0.45",
      last_login_browser: "Safari",
      last_login_device: "iPhone 15 Pro",
      created_at: new Date(Date.now() - 86400000 * 30).toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];
}

if (!globalUserStore.__axorks_sessions) {
  globalUserStore.__axorks_sessions = [];
}

export const usersStore = globalUserStore.__axorks_users;
export const sessionsStore = globalUserStore.__axorks_sessions;

export function findUserByIdentifier(identifier: string): StoredUser | undefined {
  const clean = identifier.trim().toLowerCase();
  return usersStore.find(
    (u) => u.username.toLowerCase() === clean || u.email.toLowerCase() === clean
  );
}

export function registerNewUser(data: {
  email: string;
  password: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  department?: string;
  role?: string;
  designation?: string;
  phone?: string;
}): StoredUser {
  const cleanEmail = data.email.trim().toLowerCase();
  const existing = findUserByIdentifier(cleanEmail);

  if (existing) {
    return existing;
  }

  const generatedUsername =
    data.username?.trim().toLowerCase() ||
    cleanEmail.split("@")[0].replace(/[^a-z0-9]/g, "") ||
    `user_${Date.now()}`;

  const newUser: StoredUser = {
    id: `user_${Date.now()}`,
    organization_id: "00000000-0000-0000-0000-000000000001",
    email: cleanEmail,
    username: generatedUsername,
    password: data.password,
    first_name: data.first_name || "New",
    last_name: data.last_name || "User",
    display_name: `${data.first_name || "New"} ${data.last_name || "User"}`.trim(),
    employee_id: `EMP-${Math.floor(Math.random() * 9000) + 1000}`,
    phone: data.phone || null,
    department: data.department || "Development",
    designation: data.designation || "Team Member",
    joining_date: new Date().toISOString().split("T")[0],
    employment_type: "full_time",
    role: data.role || "Software Engineer",
    status: "active",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  usersStore.unshift(newUser);
  return newUser;
}

export function recordLoginSession(user: StoredUser, ip: string = "127.0.0.1", device: string = "Desktop"): UserSession {
  user.last_login_at = new Date().toISOString();
  user.last_login_ip = ip;
  user.last_login_device = device;

  // Filter out any previous active session for this user
  const filtered = sessionsStore.filter((s) => s.user_id !== user.id);
  globalUserStore.__axorks_sessions = filtered;

  const session: UserSession = {
    session_id: `sess_${Date.now()}`,
    user_id: user.id,
    username: user.username,
    email: user.email,
    first_name: user.first_name,
    last_name: user.last_name,
    role: user.role,
    ip_address: ip,
    device,
    login_at: new Date().toISOString(),
    last_active_at: new Date().toISOString(),
  };

  globalUserStore.__axorks_sessions.unshift(session);
  return session;
}
