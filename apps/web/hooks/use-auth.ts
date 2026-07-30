"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { getAccessToken } from "@/lib/auth";

export function useAuth() {
  const token = getAccessToken();

  const { data: user, isLoading, error } = useQuery({
    queryKey: ["current-user", token],
    queryFn: () => apiClient("/api/v1/users/me"),
    enabled: !!token,
  });

  return {
    user,
    isLoading: !!token && isLoading,
    isAuthenticated: !!user,
    error,
  };
}
