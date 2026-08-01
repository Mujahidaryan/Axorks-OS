let inMemoryAccessToken: string | null = null;

export function setAccessToken(token: string | null) {
  inMemoryAccessToken = token;
}

export function getAccessToken(): string | null {
  return inMemoryAccessToken;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

interface ApiEnvelope<T = unknown> {
  data: T;
  meta?: {
    page?: number;
    per_page?: number;
    total?: number;
    total_pages?: number;
  } | null;
  errors?: Array<{ message: string }> | null;
}

async function buildRequest(endpoint: string, options: FetchOptions = {}) {
  const { params, headers, ...restOptions } = options;

  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  const token = getAccessToken();

  const reqHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string>),
  };

  if (token) {
    reqHeaders["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      headers: reqHeaders,
      ...restOptions,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message =
        errorData?.errors?.[0]?.message || errorData?.detail || `HTTP Error ${response.status}`;
      throw new Error(message);
    }

    return response;
  } catch (err: any) {
    // If direct fetch to API_BASE_URL threw a network connection error (e.g. Failed to fetch)
    // attempt relative Next.js API route fallback seamlessly
    if (
      (err.name === "TypeError" || err.message?.includes("Failed to fetch") || err.message?.includes("fetch failed")) &&
      url !== endpoint
    ) {
      let relativeUrl = endpoint;
      if (params) {
        const searchParams = new URLSearchParams(params);
        relativeUrl += `?${searchParams.toString()}`;
      }

      try {
        const fallbackResponse = await fetch(relativeUrl, {
          headers: reqHeaders,
          ...restOptions,
        });

        if (fallbackResponse.ok) {
          return fallbackResponse;
        }
      } catch (fallbackErr) {
        // Fallback failed
      }
    }
    throw err;
  }
}

export async function apiClient<T = any>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const response = await buildRequest(endpoint, options);
  const json: ApiEnvelope<T> = await response.json();
  return json.data;
}

/** Paginated list endpoints — returns full envelope with meta. */
export async function apiClientPaginated<T = any>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<ApiEnvelope<T[]>> {
  const response = await buildRequest(endpoint, options);
  return response.json();
}

/** Authenticated file download — returns Blob. */
export async function apiDownload(endpoint: string): Promise<Blob> {
  const response = await buildRequest(endpoint, { method: "GET" });
  return response.blob();
}
