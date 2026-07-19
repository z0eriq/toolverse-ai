"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Star } from "lucide-react";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Link } from "@/i18n/navigation";
import { cn } from "@/lib/utils";

export function ToolReviews({
  toolId,
  toolSlug,
}: {
  toolId: string;
  toolSlug: string;
}) {
  const t = useTranslations("reviews");
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [rating, setRating] = useState(5);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  const reviews = useQuery({
    queryKey: ["tool-reviews", toolSlug],
    queryFn: () => api.reviews({ tool: toolSlug }),
  });

  const create = useMutation({
    mutationFn: () =>
      api.createReview({
        tool_id: toolId,
        rating,
        title: title.trim(),
        body: body.trim(),
      }),
    onSuccess: async () => {
      setFormError(null);
      setFormSuccess(t("submitted"));
      setTitle("");
      setBody("");
      await queryClient.invalidateQueries({ queryKey: ["tool-reviews", toolSlug] });
    },
    onError: (err) => {
      setFormSuccess(null);
      setFormError(err instanceof ApiError ? err.message : t("error"));
    },
  });

  const list = reviews.data ?? [];
  const avg =
    list.length > 0
      ? list.reduce((sum, r) => sum + r.rating, 0) / list.length
      : 0;

  return (
    <section className="mt-16" aria-labelledby="tool-reviews-heading">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2
            id="tool-reviews-heading"
            className="font-display text-xl font-semibold"
          >
            {t("title")}
          </h2>
          {list.length > 0 ? (
            <p className="mt-1 text-sm text-[var(--muted)]">
              {t("average", {
                rating: avg.toFixed(1),
                count: list.length,
              })}
            </p>
          ) : (
            <p className="mt-1 text-sm text-[var(--muted)]">{t("empty")}</p>
          )}
        </div>
      </div>

      <ul className="mt-6 space-y-3">
        {list.map((review) => (
          <li
            key={review.id}
            className="surface rounded-[var(--radius-lg)] p-4"
          >
            <div className="flex flex-wrap items-center gap-2">
              <div className="flex" aria-label={`${review.rating} / 5`}>
                {Array.from({ length: 5 }, (_, i) => (
                  <Star
                    key={i}
                    className={cn(
                      "h-3.5 w-3.5",
                      i < review.rating
                        ? "fill-[var(--accent)] text-[var(--accent)]"
                        : "text-[var(--muted)]",
                    )}
                    aria-hidden
                  />
                ))}
              </div>
              <span className="text-sm font-medium">
                {review.title || t("untitled")}
              </span>
              <span className="text-xs text-[var(--muted)]">
                {review.user_name || t("anonymous")}
              </span>
            </div>
            {review.body ? (
              <p className="mt-2 text-sm text-[var(--muted)]">{review.body}</p>
            ) : null}
          </li>
        ))}
      </ul>

      <div className="mt-8 surface rounded-[var(--radius-lg)] p-5">
        <h3 className="font-display text-lg font-semibold">{t("write")}</h3>
        {!user ? (
          <p className="mt-2 text-sm text-[var(--muted)]">
            {t("loginRequired")}{" "}
            <Link href="/auth/login" className="text-[var(--accent)] hover:underline">
              {t("login")}
            </Link>
          </p>
        ) : (
          <form
            className="mt-4 space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              create.mutate();
            }}
          >
            <div>
              <Label htmlFor="review-rating">{t("rating")}</Label>
              <div className="mt-2 flex gap-1">
                {Array.from({ length: 5 }, (_, i) => {
                  const value = i + 1;
                  return (
                    <button
                      key={value}
                      type="button"
                      className="rounded p-1 hover:bg-[color-mix(in_oklab,var(--foreground)_6%,transparent)]"
                      aria-label={`${value}`}
                      aria-pressed={rating === value}
                      onClick={() => setRating(value)}
                    >
                      <Star
                        className={cn(
                          "h-5 w-5",
                          value <= rating
                            ? "fill-[var(--accent)] text-[var(--accent)]"
                            : "text-[var(--muted)]",
                        )}
                        aria-hidden
                      />
                    </button>
                  );
                })}
              </div>
            </div>
            <div>
              <Label htmlFor="review-title">{t("reviewTitle")}</Label>
              <Input
                id="review-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={120}
              />
            </div>
            <div>
              <Label htmlFor="review-body">{t("reviewBody")}</Label>
              <Textarea
                id="review-body"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                rows={4}
                maxLength={2000}
              />
            </div>
            {formError ? (
              <p className="text-sm text-[var(--color-danger)]" role="alert">
                {formError}
              </p>
            ) : null}
            {formSuccess ? (
              <p className="text-sm text-[var(--accent)]" role="status">
                {formSuccess}
              </p>
            ) : null}
            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? t("submitting") : t("submit")}
            </Button>
          </form>
        )}
      </div>
    </section>
  );
}
