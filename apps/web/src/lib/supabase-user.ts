import type { User } from "@supabase/supabase-js";
import type { AuthUser, UserProfile } from "@/lib/auth";

export type ProfileRow = {
  id: string;
  email: string | null;
  display_name: string;
  avatar_url: string | null;
  locale: string;
  theme: string;
  public_username: string | null;
  is_public: boolean;
  headline: string;
  bio: string;
  role: string;
  created_at: string;
  updated_at: string;
};

export function mapSupabaseUser(
  user: User,
  profile: ProfileRow | null,
): AuthUser {
  const profileMapped: UserProfile | undefined = profile
    ? {
        bio: profile.bio,
        avatar_url: profile.avatar_url ?? "",
        locale: profile.locale,
        theme: profile.theme,
        created_at: profile.created_at,
        updated_at: profile.updated_at,
      }
    : undefined;

  return {
    id: user.id,
    email: profile?.email ?? user.email ?? "",
    name:
      profile?.display_name ||
      (typeof user.user_metadata?.name === "string"
        ? user.user_metadata.name
        : "") ||
      "",
    role: profile?.role ?? "user",
    is_premium: false,
    date_joined: user.created_at,
    profile: profileMapped,
  };
}
