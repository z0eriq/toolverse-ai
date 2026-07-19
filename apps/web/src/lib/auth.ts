export type UserRole = "user" | "admin" | "staff";

export interface UserProfile {
  bio: string;
  avatar_url: string;
  locale: string;
  theme: string;
  created_at: string;
  updated_at: string;
}

export interface AuthUser {
  id: string | number;
  email: string;
  name: string;
  role: UserRole | string;
  is_premium: boolean;
  date_joined: string;
  profile?: UserProfile;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

const ACCESS_KEY = "tv_access";
const REFRESH_KEY = "tv_refresh";

let memoryAccess: string | null = null;

function canUseStorage(): boolean {
  return typeof window !== "undefined";
}

export function getAccessToken(): string | null {
  if (memoryAccess) return memoryAccess;
  if (!canUseStorage()) return null;
  try {
    memoryAccess = localStorage.getItem(ACCESS_KEY);
    return memoryAccess;
  } catch {
    return null;
  }
}

export function getRefreshToken(): string | null {
  if (!canUseStorage()) return null;
  try {
    return localStorage.getItem(REFRESH_KEY);
  } catch {
    return null;
  }
}

export function setTokens(tokens: AuthTokens): void {
  memoryAccess = tokens.access;
  if (!canUseStorage()) return;
  try {
    localStorage.setItem(ACCESS_KEY, tokens.access);
    localStorage.setItem(REFRESH_KEY, tokens.refresh);
  } catch {
    // ignore quota / private mode
  }
}

export function setAccessToken(access: string): void {
  memoryAccess = access;
  if (!canUseStorage()) return;
  try {
    localStorage.setItem(ACCESS_KEY, access);
  } catch {
    // ignore
  }
}

export function clearTokens(): void {
  memoryAccess = null;
  if (!canUseStorage()) return;
  try {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  } catch {
    // ignore
  }
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}
