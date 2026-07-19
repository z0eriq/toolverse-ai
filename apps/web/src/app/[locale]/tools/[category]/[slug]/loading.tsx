export default function ToolPageLoading() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6" aria-busy="true" aria-live="polite">
      <div className="mb-8 max-w-3xl space-y-3">
        <div className="h-3 w-20 animate-pulse rounded bg-[var(--border)]" />
        <div className="h-10 w-2/3 animate-pulse rounded bg-[var(--border)]" />
        <div className="h-4 w-full animate-pulse rounded bg-[var(--border)]" />
      </div>
      <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <div className="surface h-72 animate-pulse rounded-[var(--radius-lg)] p-6" aria-hidden>
          <div className="h-4 w-1/3 rounded bg-[var(--border)]" />
          <div className="mt-4 h-32 rounded bg-[var(--border)]" />
          <div className="mt-4 h-10 w-28 rounded bg-[var(--border)]" />
        </div>
        <div className="h-48 animate-pulse rounded-[var(--radius-lg)] bg-[var(--border)]" />
      </div>
      <span className="sr-only">Loading tool…</span>
    </div>
  );
}
