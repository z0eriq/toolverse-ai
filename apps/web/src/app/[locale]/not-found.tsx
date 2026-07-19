import { Link } from "@/i18n/navigation";

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[60vh] max-w-lg flex-col items-center justify-center px-4 text-center">
      <p className="text-sm font-semibold uppercase tracking-wider text-[var(--accent)]">404</p>
      <h1 className="mt-3 font-display text-3xl font-semibold tracking-tight">Page not found</h1>
      <p className="mt-2 text-[var(--muted)]">
        The page you are looking for does not exist or has moved.
      </p>
      <Link
        href="/"
        className="mt-8 inline-flex h-10 items-center rounded-[var(--radius-md)] bg-[var(--accent)] px-4 text-sm font-medium text-[var(--accent-fg)]"
      >
        Back home
      </Link>
    </div>
  );
}
