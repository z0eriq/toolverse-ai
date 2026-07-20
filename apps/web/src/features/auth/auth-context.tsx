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
import { createClient } from "@/utils/supabase/client";
import { clearTokens } from "@/lib/auth";
import type { AuthUser } from "@/lib/auth";
import { mapSupabaseUser, type ProfileRow } from "@/lib/supabase-user";

export class AuthNeedsConfirmationError extends Error {
  constructor() {
    super("EMAIL_CONFIRMATION_REQUIRED");
    this.name = "AuthNeedsConfirmationError";
  }
}

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

async function loadProfile(
  userId: string,
): Promise<ProfileRow | null> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("profiles")
    .select(
      "id, email, display_name, avatar_url, locale, theme, public_username, is_public, headline, bio, role, created_at, updated_at",
    )
    .eq("id", userId)
    .maybeSingle();

  if (error) {
    console.warn("[auth] profiles fetch failed", error.message);
    return null;
  }
  return data as ProfileRow | null;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const supabase = createClient();
    const {
      data: { user: authUser },
    } = await supabase.auth.getUser();

    if (!authUser) {
      setUser(null);
      return;
    }

    const profile = await loadProfile(authUser.id);
    setUser(mapSupabaseUser(authUser, profile));
  }, []);

  useEffect(() => {
    const supabase = createClient();
    let mounted = true;

    void (async () => {
      try {
        await refreshUser();
      } finally {
        if (mounted) setIsLoading(false);
      }
    })();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      void refreshUser();
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [refreshUser]);

  const login = useCallback(async (email: string, password: string) => {
    const supabase = createClient();
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
    // Django JWT tokens are unused for session now.
    clearTokens();
    await refreshUser();
  }, [refreshUser]);

  const register = useCallback(
    async (input: { email: string; name: string; password: string }) => {
      const supabase = createClient();
      const origin =
        typeof window !== "undefined" ? window.location.origin : "";
      const locale =
        typeof window !== "undefined"
          ? window.location.pathname.split("/")[1] || "en"
          : "en";

      const { data, error } = await supabase.auth.signUp({
        email: input.email,
        password: input.password,
        options: {
          data: { name: input.name },
          emailRedirectTo: `${origin}/auth/callback?next=/${locale}/dashboard`,
        },
      });
      if (error) throw error;

      clearTokens();

      if (!data.session) {
        throw new AuthNeedsConfirmationError();
      }

      await refreshUser();
    },
    [refreshUser],
  );

  const logout = useCallback(async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    clearTokens();
    setUser(null);
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
