import { Link } from "@/i18n/navigation";
import { SATELLITE_KINDS, satelliteLabel, type SatelliteKind } from "@/lib/tool-satellites";

export function ToolSatelliteNav({
  category,
  slug,
  locale,
  active,
}: {
  category: string;
  slug: string;
  locale: string;
  active?: SatelliteKind | "main";
}) {
  const base = `/tools/${category}/${slug}`;
  return (
    <nav aria-label="Tool pages" className="flex flex-wrap gap-2 text-sm">
      <Link
        href={base}
        className={`rounded-full border px-3 py-1 transition ${
          active === "main" || !active
            ? "border-[var(--accent)] text-[var(--accent)]"
            : "border-[var(--border)] text-[var(--muted)] hover:text-[var(--fg)]"
        }`}
      >
        {locale === "ar" ? "الأداة" : "Tool"}
      </Link>
      {SATELLITE_KINDS.map((kind) => (
        <Link
          key={kind}
          href={`${base}/${kind}`}
          className={`rounded-full border px-3 py-1 transition ${
            active === kind
              ? "border-[var(--accent)] text-[var(--accent)]"
              : "border-[var(--border)] text-[var(--muted)] hover:text-[var(--fg)]"
          }`}
        >
          {satelliteLabel(kind, locale)}
        </Link>
      ))}
    </nav>
  );
}
