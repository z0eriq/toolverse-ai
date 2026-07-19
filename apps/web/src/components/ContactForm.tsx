"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function ContactForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "ok" | "error">(
    "idle",
  );
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("sending");
    setError("");
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, message }),
      });
      const json = (await res.json()) as { success?: boolean; error?: string };
      if (!res.ok || !json.success) {
        setStatus("error");
        setError(json.error || "Could not send your message. Try again.");
        return;
      }
      setStatus("ok");
      setName("");
      setEmail("");
      setMessage("");
    } catch {
      setStatus("error");
      setError("Network error. Email us at support@tool-verse.online.");
    }
  }

  return (
    <form onSubmit={onSubmit} className="mt-8 space-y-4" noValidate>
      <div>
        <Label htmlFor="contact-name">Name</Label>
        <Input
          id="contact-name"
          name="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          maxLength={120}
          autoComplete="name"
          className="mt-1.5"
        />
      </div>
      <div>
        <Label htmlFor="contact-email">Email</Label>
        <Input
          id="contact-email"
          name="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          maxLength={254}
          autoComplete="email"
          className="mt-1.5"
        />
      </div>
      <div>
        <Label htmlFor="contact-message">Message</Label>
        <textarea
          id="contact-message"
          name="message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          required
          minLength={10}
          maxLength={5000}
          rows={6}
          className="mt-1.5 w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-transparent px-3 py-2 text-sm outline-none focus-visible:border-[var(--accent)]"
        />
      </div>
      {status === "ok" ? (
        <p className="text-sm text-[var(--accent)]" role="status">
          Thanks — we received your message. We typically reply within 1–2
          business days.
        </p>
      ) : null}
      {status === "error" ? (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}
      <Button type="submit" disabled={status === "sending"}>
        {status === "sending" ? "Sending…" : "Send message"}
      </Button>
    </form>
  );
}
