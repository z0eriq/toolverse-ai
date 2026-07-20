"use client";

import { useTranslations } from "next-intl";
import { Menu, Search, X } from "lucide-react";
import { useState } from "react";
import { Link } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LocaleSwitcher } from "@/components/LocaleSwitcher";
import { SearchCommand } from "@/components/SearchCommand";
import { useAuth } from "@/features/auth/auth-context";
import { cn } from "@/lib/utils";

export function Header() {
  const t = useTranslations("nav");
  const { user, logout, isLoading } = useAuth();
  const [open, setOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  const links = [
    { href: "/#tools", label: t("tools") },
    { href: "/pricing", label: t("pricing") },
    { href: "/blog", label: t("blog") },
    { href: "/developers", label: t("developers") },
  ] as const;

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-[var(--border)]/80 bg-[color-mix(in_oklab,var(--background)_82%,transparent)] backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
          <Link href="/" className="font-display text-lg font-semibold tracking-tight">
            <span className="text-gradient">ToolVerse</span>
            <span className="ms-1 text-[var(--foreground)]">AI</span>
          </Link>

          <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-[var(--radius-md)] px-3 py-2 text-sm text-[var(--muted)] transition hover:bg-[color-mix(in_oklab,var(--foreground)_6%,transparent)] hover:text-[var(--foreground)]"
              >
                {link.label}
              </Link>
            ))}
            {user ? (
              <>
                <Link
                  href="/dashboard"
                  className="rounded-[var(--radius-md)] px-3 py-2 text-sm text-[var(--muted)] transition hover:text-[var(--foreground)]"
                >
                  {t("dashboard")}
                </Link>
                <Link
                  href="/workspace"
                  className="rounded-[var(--radius-md)] px-3 py-2 text-sm text-[var(--muted)] transition hover:text-[var(--foreground)]"
                >
                  {t("workspace")}
                </Link>
              </>
            ) : null}
          </nav>

          <div className="flex items-center gap-1.5">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label={t("search")}
              onClick={() => setSearchOpen(true)}
            >
              <Search className="h-4 w-4" aria-hidden />
            </Button>
            <LocaleSwitcher />
            <ThemeToggle />
            <div className="hidden items-center gap-2 sm:flex">
              {!isLoading && !user ? (
                <>
                  <Button asChild variant="ghost" size="sm">
                    <Link href="/auth/login">{t("login")}</Link>
                  </Button>
                  <Button asChild size="sm">
                    <Link href="/auth/register">{t("register")}</Link>
                  </Button>
                </>
              ) : null}
              {user ? (
                <Button type="button" variant="secondary" size="sm" onClick={() => void logout()}>
                  {t("logout")}
                </Button>
              ) : null}
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="md:hidden"
              aria-label="Menu"
              aria-expanded={open}
              onClick={() => setOpen((v) => !v)}
            >
              {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        <div
          className={cn(
            "border-t border-[var(--border)] md:hidden",
            open ? "block" : "hidden",
          )}
        >
          <div className="mx-auto flex max-w-6xl flex-col gap-1 px-4 py-3">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-[var(--radius-md)] px-3 py-2 text-sm"
                onClick={() => setOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            {user ? (
              <>
                <Link
                  href="/dashboard"
                  className="rounded-[var(--radius-md)] px-3 py-2 text-sm"
                  onClick={() => setOpen(false)}
                >
                  {t("dashboard")}
                </Link>
                <Link
                  href="/workspace"
                  className="rounded-[var(--radius-md)] px-3 py-2 text-sm"
                  onClick={() => setOpen(false)}
                >
                  {t("workspace")}
                </Link>
                <Link
                  href="/favorites"
                  className="rounded-[var(--radius-md)] px-3 py-2 text-sm"
                  onClick={() => setOpen(false)}
                >
                  {t("favorites")}
                </Link>
                <Link
                  href="/history"
                  className="rounded-[var(--radius-md)] px-3 py-2 text-sm"
                  onClick={() => setOpen(false)}
                >
                  {t("history")}
                </Link>
              </>
            ) : (
              <>
                <Link
                  href="/auth/login"
                  className="rounded-[var(--radius-md)] px-3 py-2 text-sm"
                  onClick={() => setOpen(false)}
                >
                  {t("login")}
                </Link>
                <Link
                  href="/auth/register"
                  className="rounded-[var(--radius-md)] px-3 py-2 text-sm"
                  onClick={() => setOpen(false)}
                >
                  {t("register")}
                </Link>
              </>
            )}
          </div>
        </div>
      </header>
      <SearchCommand open={searchOpen} onOpenChange={setSearchOpen} />
    </>
  );
}
