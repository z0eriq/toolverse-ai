"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  api,
  type DynamicUiField,
  type DynamicUiSchema,
} from "@/lib/api";
import { useJobPoll } from "@/lib/use-job-poll";
import { useToolHistory } from "@/lib/use-tool-history";
import { isAuthenticated } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { CopyButton } from "@/components/ui/copy-button";
import { ToolPanel } from "@/components/ui/tool-panel";
import { PremiumGate } from "@/components/PremiumGate";

const DEFAULT_FIELDS: DynamicUiField[] = [
  {
    name: "input",
    type: "textarea",
    label: "Input",
    placeholder: "Enter input…",
    required: true,
  },
];

function normalizeFields(schema?: DynamicUiSchema | null): DynamicUiField[] {
  if (schema?.fields && Array.isArray(schema.fields) && schema.fields.length > 0) {
    return schema.fields.filter((f) => f && typeof f.name === "string");
  }
  return DEFAULT_FIELDS;
}

function initialValues(fields: DynamicUiField[]): Record<string, string | number | boolean> {
  const values: Record<string, string | number | boolean> = {};
  for (const field of fields) {
    if (field.defaultValue !== undefined) {
      values[field.name] = field.defaultValue;
    } else if (field.type === "checkbox") {
      values[field.name] = false;
    } else if (field.type === "number") {
      values[field.name] = "";
    } else {
      values[field.name] = "";
    }
  }
  return values;
}

function formatOutput(output: unknown): string {
  if (output == null) return "";
  if (typeof output === "string") return output;
  try {
    return JSON.stringify(output, null, 2);
  } catch {
    return String(output);
  }
}

export interface DynamicToolRuntimeProps {
  slug: string;
  toolId: string;
  uiSchema?: DynamicUiSchema | null;
  capabilities?: string[];
}

export function DynamicToolRuntime({
  slug,
  toolId,
  uiSchema,
  capabilities = [],
}: DynamicToolRuntimeProps) {
  const t = useTranslations("tool");
  const { record } = useToolHistory(toolId);
  const fields = useMemo(() => normalizeFields(uiSchema), [uiSchema]);
  const [values, setValues] = useState(() => initialValues(fields));
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [limitExceeded, setLimitExceeded] = useState(false);
  const [running, setRunning] = useState(false);
  const supportsAsync = capabilities.includes("async");
  const { job, error: pollError, isPolling, start, reset } = useJobPoll({
    onComplete: (completed) => {
      if (completed.status === "succeeded") {
        setOutput(formatOutput(completed.output_payload));
        void record("run", { mode: "async", job_id: completed.id });
      } else {
        setError(completed.error || t("error"));
      }
      setRunning(false);
    },
  });

  useEffect(() => {
    setValues(initialValues(fields));
  }, [fields]);

  const submitLabel =
    (typeof uiSchema?.submitLabel === "string" && uiSchema.submitLabel) || t("run");

  const onFieldChange = useCallback((name: string, value: string | number | boolean) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  }, []);

  const buildInput = useCallback((): Record<string, unknown> => {
    const input: Record<string, unknown> = {};
    for (const field of fields) {
      const raw = values[field.name];
      if (field.type === "number" && raw !== "" && raw !== undefined) {
        input[field.name] = Number(raw);
      } else {
        input[field.name] = raw;
      }
    }
    return input;
  }, [fields, values]);

  const validate = useCallback((): string | null => {
    for (const field of fields) {
      if (!field.required) continue;
      const raw = values[field.name];
      if (raw === "" || raw === undefined || raw === null) {
        return `${field.label || field.name} is required`;
      }
    }
    return null;
  }, [fields, values]);

  const handleRun = useCallback(async () => {
    setError(null);
    setLimitExceeded(false);
    reset();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    const input = buildInput();
    setRunning(true);
    setOutput("");

    try {
      if (supportsAsync && isAuthenticated()) {
        const created = await api.createJob(toolId, input);
        start(created.id);
        return;
      }

      const result = await api.runDynamicTool(slug, input);
      setOutput(formatOutput(result.output));
      void record("run", { mode: "sync" });
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setLimitExceeded(true);
      }
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("error");
      setError(message);
    } finally {
      if (!(supportsAsync && isAuthenticated())) {
        setRunning(false);
      }
    }
  }, [
    buildInput,
    record,
    reset,
    slug,
    start,
    supportsAsync,
    t,
    toolId,
    validate,
  ]);

  const busy = running || isPolling;
  const progress = job?.progress ?? 0;

  if (limitExceeded) {
    return (
      <PremiumGate limitExceeded>
        <ToolPanel>
          <p className="text-sm text-[var(--muted)]">{error}</p>
        </ToolPanel>
      </PremiumGate>
    );
  }

  return (
    <ToolPanel>
      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          void handleRun();
        }}
      >
        {fields.map((field) => (
          <div key={field.name}>
            <Label htmlFor={`dyn-${field.name}`}>
              {field.label || field.name}
              {field.required ? (
                <span className="ms-1 text-[var(--color-danger)]" aria-hidden>
                  *
                </span>
              ) : null}
            </Label>
            {field.type === "textarea" ? (
              <Textarea
                id={`dyn-${field.name}`}
                name={field.name}
                placeholder={field.placeholder}
                value={String(values[field.name] ?? "")}
                onChange={(e) => onFieldChange(field.name, e.target.value)}
                required={field.required}
                rows={8}
              />
            ) : field.type === "select" && field.options?.length ? (
              <select
                id={`dyn-${field.name}`}
                name={field.name}
                className="flex h-10 w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--card)] px-3 text-sm"
                value={String(values[field.name] ?? "")}
                onChange={(e) => onFieldChange(field.name, e.target.value)}
                required={field.required}
              >
                <option value="">Select…</option>
                {field.options.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            ) : field.type === "checkbox" ? (
              <label className="flex items-center gap-2 text-sm">
                <input
                  id={`dyn-${field.name}`}
                  type="checkbox"
                  checked={Boolean(values[field.name])}
                  onChange={(e) => onFieldChange(field.name, e.target.checked)}
                />
                {field.placeholder || field.label || field.name}
              </label>
            ) : (
              <Input
                id={`dyn-${field.name}`}
                name={field.name}
                type={field.type === "number" ? "number" : "text"}
                placeholder={field.placeholder}
                value={String(values[field.name] ?? "")}
                onChange={(e) =>
                  onFieldChange(
                    field.name,
                    field.type === "number" ? e.target.value : e.target.value,
                  )
                }
                required={field.required}
              />
            )}
          </div>
        ))}

        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" disabled={busy}>
            {busy ? t("running") : submitLabel}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={busy && !output}
            onClick={() => {
              setValues(initialValues(fields));
              setOutput("");
              setError(null);
              reset();
            }}
          >
            {t("clear")}
          </Button>
          {supportsAsync ? (
            <p className="text-xs text-[var(--muted)]">
              {isAuthenticated()
                ? t("asyncHint")
                : t("asyncLoginHint")}
            </p>
          ) : null}
        </div>

        {isPolling ? (
          <div className="space-y-1" aria-live="polite">
            <p className="text-xs text-[var(--muted)]">
              {t("jobStatus")}: {job?.status ?? "queued"} ({progress}%)
            </p>
            <div className="h-2 overflow-hidden rounded-full bg-[color-mix(in_oklab,var(--foreground)_8%,transparent)]">
              <div
                className="h-full rounded-full bg-[var(--accent)] transition-all"
                style={{ width: `${Math.min(100, Math.max(4, progress))}%` }}
              />
            </div>
          </div>
        ) : null}

        {error || pollError ? (
          <p className="text-sm text-[var(--color-danger)]" role="alert">
            {error || pollError}
          </p>
        ) : null}

        {output ? (
          <div>
            <div className="mb-1.5 flex items-center justify-between gap-2">
              <Label htmlFor="dyn-output">{t("output")}</Label>
              <CopyButton value={output} />
            </div>
            <Textarea id="dyn-output" readOnly value={output} rows={10} />
          </div>
        ) : null}
      </form>
    </ToolPanel>
  );
}
