export * from "./api";

export interface User {
  id: string;
  email: string;
  email_verified: boolean;
  first_name?: string;
  last_name?: string;
  avatar_url?: string;
  phone?: string;
  timezone: string;
  locale: string;
  preferences: Record<string, any>;
  two_factor_enabled: boolean;
  last_login_at?: string;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  plan: string;
  settings: Record<string, any>;
  created_at: string;
}

export interface Workspace {
  id: string;
  organization_id: string;
  name: string;
  slug: string;
  is_default: boolean;
  settings: Record<string, any>;
  created_at: string;
}

export interface NotificationItem {
  id: string;
  type: string;
  title: string;
  body?: string;
  link?: string;
  read_at?: string;
  created_at: string;
}

export interface SearchResultItem {
  id: string;
  type: string;
  title: string;
  subtitle?: string;
  link: string;
}
