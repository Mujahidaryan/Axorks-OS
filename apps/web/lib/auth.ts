import { apiClient, setAccessToken } from "./api-client";

export async function login(email: string, password: str) {
  const data = await apiClient("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  if (data.access_token) {
    setAccessToken(data.access_token);
  }
  return data;
}

export async function register(params: {
  email: string;
  password: str;
  first_name?: string;
  last_name?: string;
}) {
  const data = await apiClient("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(params),
  });
  if (data.access_token) {
    setAccessToken(data.access_token);
  }
  return data;
}

export async function logout() {
  try {
    await apiClient("/api/v1/auth/logout", { method: "POST" });
  } finally {
    setAccessToken(null);
  }
}
