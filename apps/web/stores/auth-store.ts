"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { setAccessToken as setGlobalAccessToken } from "@/lib/api-client";

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  department?: string;
  avatar_url?: string | null;
}

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  setAuth: (user: AuthUser, accessToken: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      setAuth: (user, accessToken) => {
        setGlobalAccessToken(accessToken);
        set({ user, accessToken, isAuthenticated: true });
      },
      logout: () => {
        setGlobalAccessToken(null);
        set({ user: null, accessToken: null, isAuthenticated: false });
      },
    }),
    {
      name: "axorks_auth_session",
      onRehydrateStorage: () => (state) => {
        if (state?.accessToken) {
          setGlobalAccessToken(state.accessToken);
        }
      },
    }
  )
);
