export default function HomeLoading() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6" aria-busy="true" aria-live="polite">
      <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-4">
          <div className="h-4 w-24 animate-pulse rounded bg-[var(--border)]" />
          <div className="h-12 w-3/4 animate-pulse rounded bg-[var(--border)]" />
          <div className="h-4 w-full max-w-md animate-pulse rounded bg-[var(--border)]" />
          <div className="mt-6 flex gap-3">
            <div className="h-11 w-32 animate-pulse rounded-[var(--radius-md)] bg-[var(--border)]" />
            <div className="h-11 w-32 animate-pulse rounded-[var(--radius-md)] bg-[var(--border)]" />
          </div>
        </div>
        <div className="h-64 animate-pulse rounded-[var(--radius-lg)] bg-[var(--border)]" />
      </div>
      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="surface h-36 animate-pulse rounded-[var(--radius-lg)] p-4"
            aria-hidden
          >
            <div className="h-3 w-16 rounded bg-[var(--border)]" />
            <div className="mt-3 h-5 w-2/3 rounded bg-[var(--border)]" />
            <div className="mt-2 h-3 w-full rounded bg-[var(--border)]" />
          </div>
        ))}
      </div>
      <span className="sr-only">Loading…</span>
    </div>
  );
}
