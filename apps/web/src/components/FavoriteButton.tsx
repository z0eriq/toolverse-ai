"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Star } from "lucide-react";
import { useTranslations } from "next-intl";
import { api } from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";

export function FavoriteButton({ toolId }: { toolId: string }) {
  const t = useTranslations("tool");
  const { user } = useAuth();
  const qc = useQueryClient();

  const favorites = useQuery({
    queryKey: ["favorites"],
    queryFn: () => api.favorites(),
    enabled: Boolean(user),
  });

  const isFavorite = (favorites.data ?? []).some((f) => f.tool.tool_id === toolId);

  const toggle = useMutation({
    mutationFn: async () => {
      if (isFavorite) await api.removeFavorite(toolId);
      else await api.addFavorite(toolId);
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["favorites"] });
    },
  });

  if (!user) {
    return (
      <Button asChild variant="secondary" size="sm">
        <Link href="/auth/login">{t("favorite")}</Link>
      </Button>
    );
  }

  return (
    <Button
      type="button"
      variant={isFavorite ? "primary" : "secondary"}
      size="sm"
      disabled={toggle.isPending}
      onClick={() => toggle.mutate()}
      aria-pressed={isFavorite}
    >
      <Star className="h-4 w-4" fill={isFavorite ? "currentColor" : "none"} aria-hidden />
      {isFavorite ? t("unfavorite") : t("favorite")}
    </Button>
  );
}
