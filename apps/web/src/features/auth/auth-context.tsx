"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  api,
  clearTokens,
  getRefreshToken,
  setTokens,
} from "@/lib/api";
import { getAccessToken, type AuthUser } from "@/lib/auth";

interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (input: {
    email: string;
    name: string;
    password: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null);
      return;
    }
    try {
      const me = await api.me();
      setUser(me);
    } catch {
      clearTokens();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    void (async () => {
      try {
        await refreshUser();
      } finally {
        setIsLoading(false);
      }
    })();
  }, [refreshUser]);

  const login = useCallback(async (email: string, password: string) => {
    const result = await api.login(email, password);
    const access = "access" in result ? result.access : undefined;
    const refresh = "refresh" in result ? result.refresh : undefined;
    if (!access || !refresh) {
      throw new Error("Invalid login response");
    }
    setTokens({ access, refresh });
    if (result.user) {
      setUser(result.user);
    } else {
      await refreshUser();
    }
  }, [refreshUser]);

  const register = useCallback(
    async (input: { email: string; name: string; password: string }) => {
      const result = await api.register(input);
      setTokens(result.tokens);
      setUser(result.user);
    },
    [],
  );

  const logout = useCallback(async () => {
    const refresh = getRefreshToken();
    try {
      if (refresh) await api.logout(refresh);
    } catch {
      // ignore
    } finally {
      clearTokens();
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({ user, isLoading, login, register, logout, refreshUser }),
    [user, isLoading, login, register, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
