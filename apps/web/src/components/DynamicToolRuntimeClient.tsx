"use client";

import dynamic from "next/dynamic";
import type { DynamicToolRuntimeProps } from "@/components/DynamicToolRuntime";

const Runtime = dynamic(
  () =>
    import("@/components/DynamicToolRuntime").then((mod) => mod.DynamicToolRuntime),
  {
    ssr: false,
    loading: () => (
      <div
        className="surface animate-pulse rounded-[var(--radius-lg)] p-6"
        aria-hidden
      >
        <div className="h-4 w-1/3 rounded bg-[var(--border)]" />
        <div className="mt-4 h-24 rounded bg-[var(--border)]" />
        <div className="mt-4 h-10 w-28 rounded bg-[var(--border)]" />
      </div>
    ),
  },
);

export function DynamicToolRuntimeClient(props: DynamicToolRuntimeProps) {
  return <Runtime {...props} />;
}
