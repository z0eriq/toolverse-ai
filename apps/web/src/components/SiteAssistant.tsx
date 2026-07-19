"use client";

import { useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { MessageCircle, Send, X } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { ApiError, api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { cn, localize } from "@/lib/utils";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  tools?: {
    slug?: string;
    category?: string;
    name?: Record<string, string> | string;
  }[];
  suggestedCta?: { href: string; label: string };
};

export function SiteAssistant() {
  const t = useTranslations("assistant");
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<number | undefined>();
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: t("welcome") },
  ]);

  const chat = useMutation({
    mutationFn: (message: string) =>
      api.assistantChat({
        message,
        locale,
        session_id: sessionId,
        persist: true,
      }),
    onSuccess: (data) => {
      if (data.session_id) setSessionId(data.session_id);
      const cta = data.meta?.suggested_cta;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply,
          tools: data.recommended_tools ?? [],
          suggestedCta:
            cta &&
            typeof cta.href === "string" &&
            typeof cta.label === "string"
              ? { href: cta.href, label: cta.label }
              : undefined,
        },
      ]);
    },
    onError: (err) => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            err instanceof ApiError ? err.message : t("error"),
        },
      ]);
    },
  });

  function send() {
    const message = input.trim();
    if (!message || chat.isPending) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    chat.mutate(message);
  }

  return (
    <div className="fixed bottom-4 end-4 z-[60] flex flex-col items-end gap-3">
      {open ? (
        <div
          className="surface flex h-[min(28rem,70vh)] w-[min(22rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-[var(--radius-lg)] border border-[var(--border)] shadow-lg"
          role="dialog"
          aria-label={t("title")}
        >
          <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3">
            <div>
              <p className="font-display text-sm font-semibold">{t("title")}</p>
              <p className="text-xs text-[var(--muted)]">{t("supporting")}</p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label={t("close")}
              onClick={() => setOpen(false)}
            >
              <X className="h-4 w-4" aria-hidden />
            </Button>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
            {messages.map((msg, index) => (
              <div
                key={`${msg.role}-${index}`}
                className={cn(
                  "max-w-[90%] rounded-[var(--radius-md)] px-3 py-2 text-sm",
                  msg.role === "user"
                    ? "ms-auto bg-[var(--accent)] text-[var(--accent-fg)]"
                    : "bg-[color-mix(in_oklab,var(--foreground)_6%,transparent)] text-[var(--foreground)]",
                )}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.tools && msg.tools.length > 0 ? (
                  <ul className="mt-2 space-y-1 border-t border-[var(--border)]/60 pt-2">
                    {msg.tools.slice(0, 4).map((tool) => {
                      const slug = tool.slug;
                      const category = tool.category ?? "developer";
                      if (!slug) return null;
                      const name =
                        typeof tool.name === "string"
                          ? tool.name
                          : localize(tool.name, locale) || slug;
                      return (
                        <li key={slug}>
                          <Link
                            href={`/tools/${category}/${slug}`}
                            className="text-[var(--accent)] underline-offset-2 hover:underline"
                            onClick={() => setOpen(false)}
                          >
                            {name}
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                ) : null}
                {msg.suggestedCta ? (
                  <div className="mt-3 border-t border-[var(--border)]/60 pt-2">
                    <Button asChild size="sm" className="w-full">
                      <Link
                        href={msg.suggestedCta.href}
                        onClick={() => setOpen(false)}
                      >
                        {msg.suggestedCta.label}
                      </Link>
                    </Button>
                  </div>
                ) : null}
              </div>
            ))}
            {chat.isPending ? (
              <p className="text-xs text-[var(--muted)]">{t("thinking")}</p>
            ) : null}
          </div>

          <form
            className="flex gap-2 border-t border-[var(--border)] p-3"
            onSubmit={(e) => {
              e.preventDefault();
              send();
            }}
          >
            <label className="sr-only" htmlFor="assistant-input">
              {t("placeholder")}
            </label>
            <input
              id="assistant-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t("placeholder")}
              className="h-10 flex-1 rounded-[var(--radius-md)] border border-[var(--border)] bg-transparent px-3 text-sm outline-none focus-visible:border-[var(--accent)]"
              maxLength={2000}
              disabled={chat.isPending}
            />
            <Button
              type="submit"
              size="icon"
              disabled={chat.isPending || !input.trim()}
              aria-label={t("send")}
            >
              <Send className="h-4 w-4" aria-hidden />
            </Button>
          </form>
        </div>
      ) : null}

      <Button
        type="button"
        size="lg"
        className="rounded-full shadow-lg"
        aria-expanded={open}
        aria-label={open ? t("close") : t("open")}
        onClick={() => setOpen((v) => !v)}
      >
        <MessageCircle className="h-5 w-5" aria-hidden />
        <span className="hidden sm:inline">{t("open")}</span>
      </Button>
    </div>
  );
}
