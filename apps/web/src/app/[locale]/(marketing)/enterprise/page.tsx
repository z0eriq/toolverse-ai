"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ApiError, api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link } from "@/i18n/navigation";

export default function EnterprisePage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  const submit = useMutation({
    mutationFn: () =>
      api.salesLeads.create({
        name: name.trim(),
        email: email.trim(),
        company: company.trim(),
        role: role.trim(),
        message: message.trim(),
        intent: "demo",
      }),
    onSuccess: () => {
      setStatus("Thanks — we’ll be in touch shortly.");
      setName("");
      setEmail("");
      setCompany("");
      setRole("");
      setMessage("");
    },
    onError: (err) => {
      setStatus(err instanceof ApiError ? err.message : "Could not submit request.");
    },
  });

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <div className="max-w-2xl">
        <p className="text-sm font-medium uppercase tracking-wider text-[var(--accent)]">
          Enterprise
        </p>
        <h1 className="mt-2 font-display text-4xl font-semibold tracking-tight">
          ToolVerse AI for teams
        </h1>
        <p className="mt-3 text-[var(--muted)]">
          Higher API quotas, organization billing stubs, SSO-ready architecture,
          and dedicated support for product and growth teams.
        </p>
        <ul className="mt-6 list-disc space-y-2 ps-5 text-sm text-[var(--muted)]">
          <li>Developer organizations with enterprise plan tier</li>
          <li>Usage analytics and invoice stubs</li>
          <li>OpenAPI schema for code generation</li>
          <li>Priority rate limits and Pro-aligned tooling</li>
        </ul>
        <p className="mt-4 text-sm">
          <Link href="/developers" className="text-[var(--accent)] hover:underline">
            Open developer portal →
          </Link>
        </p>
      </div>

      <Card className="mt-12 max-w-xl">
        <h2 className="font-display text-xl font-semibold">Request a demo</h2>
        <form
          className="mt-6 space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            submit.mutate();
          }}
        >
          <div>
            <Label htmlFor="ent-name">Name</Label>
            <Input
              id="ent-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="ent-email">Work email</Label>
            <Input
              id="ent-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="ent-company">Company</Label>
            <Input
              id="ent-company"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="ent-role">Role</Label>
            <Input
              id="ent-role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="ent-message">Message</Label>
            <textarea
              id="ent-message"
              className="mt-1 min-h-[100px] w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-transparent p-3 text-sm"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </div>
          <Button type="submit" disabled={submit.isPending}>
            {submit.isPending ? "Sending…" : "Request demo"}
          </Button>
        </form>
        {status ? (
          <p className="mt-4 text-sm text-[var(--muted)]" role="status">
            {status}
          </p>
        ) : null}
      </Card>
    </div>
  );
}
