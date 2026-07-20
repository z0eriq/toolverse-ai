"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { useRouter, Link } from "@/i18n/navigation";
import {
  AuthNeedsConfirmationError,
  useAuth,
} from "@/features/auth/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const schema = z
  .object({
    name: z.string().min(1),
    email: z.string().email(),
    password: z.string().min(8),
    confirmPassword: z.string().min(8),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "match",
    path: ["confirmPassword"],
  });

type FormValues = z.infer<typeof schema>;

export function RegisterForm() {
  const t = useTranslations("auth");
  const { register: registerUser } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [confirmHint, setConfirmHint] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", email: "", password: "", confirmPassword: "" },
  });

  async function onSubmit(values: FormValues) {
    setError(null);
    setConfirmHint(null);
    try {
      await registerUser({
        email: values.email,
        name: values.name,
        password: values.password,
      });
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof AuthNeedsConfirmationError) {
        setConfirmHint(t("confirmEmail"));
        return;
      }
      setError(t("errors.generic"));
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
      <div>
        <Label htmlFor="name">{t("name")}</Label>
        <Input id="name" autoComplete="name" {...register("name")} />
        {errors.name ? (
          <p className="mt-1 text-xs text-[var(--color-danger)]" role="alert">
            {t("errors.required")}
          </p>
        ) : null}
      </div>
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
          autoComplete="new-password"
          {...register("password")}
        />
        {errors.password ? (
          <p className="mt-1 text-xs text-[var(--color-danger)]" role="alert">
            {t("errors.passwordMin")}
          </p>
        ) : null}
      </div>
      <div>
        <Label htmlFor="confirmPassword">{t("confirmPassword")}</Label>
        <Input
          id="confirmPassword"
          type="password"
          autoComplete="new-password"
          {...register("confirmPassword")}
        />
        {errors.confirmPassword ? (
          <p className="mt-1 text-xs text-[var(--color-danger)]" role="alert">
            {t("errors.passwordMatch")}
          </p>
        ) : null}
      </div>
      {confirmHint ? (
        <p className="text-sm text-[var(--muted)]" role="status">
          {confirmHint}
        </p>
      ) : null}
      {error ? (
        <p className="text-sm text-[var(--color-danger)]" role="alert">
          {error}
        </p>
      ) : null}
      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "…" : t("submitRegister")}
      </Button>
      <p className="text-center text-sm text-[var(--muted)]">
        {t("hasAccount")}{" "}
        <Link href="/auth/login" className="text-[var(--accent)] hover:underline">
          {t("submitLogin")}
        </Link>
      </p>
    </form>
  );
}
