"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { useAuth } from "@/features/auth/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link } from "@/i18n/navigation";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormValues = z.infer<typeof schema>;

export function LoginForm() {
  const t = useTranslations("auth");
  const { login } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await login(values.email, values.password);
      router.push("/dashboard");
    } catch {
      setError(t("errors.generic"));
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
      <div>
        <Label htmlFor="email">{t("email")}</Label>
        <Input id="email" type="email" autoComplete="email" {...register("email")} />
        {errors.email ? (
          <p className="mt-1 text-xs text-[var(--color-danger)]" role="alert">
            {t("errors.email")}
          </p>
        ) : null}
      </div>
      <div>
        <Label htmlFor="password">{t("password")}</Label>
        <Input
          id="password"
          type="password"
          autoComplete="current-password"
          {...register("password")}
        />
        {errors.password ? (
          <p className="mt-1 text-xs text-[var(--color-danger)]" role="alert">
            {t("errors.passwordMin")}
          </p>
        ) : null}
      </div>
      {error ? (
        <p className="text-sm text-[var(--color-danger)]" role="alert">
          {error}
        </p>
      ) : null}
      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "…" : t("submitLogin")}
      </Button>
      <p className="text-center text-sm text-[var(--muted)]">
        {t("noAccount")}{" "}
        <Link href="/auth/register" className="text-[var(--accent)] hover:underline">
          {t("submitRegister")}
        </Link>
      </p>
    </form>
  );
}
