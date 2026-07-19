import type { ToolGuide } from "@/content/tool-guides";

export function ToolEditorial({
  name,
  guide,
}: {
  name: string;
  guide: ToolGuide;
}) {
  const whatIsParagraphs = guide.whatIs
    .split(/\n\n+/)
    .map((p) => p.trim())
    .filter(Boolean);

  const updatedLabel = new Date(guide.updatedAt + "T00:00:00").toLocaleDateString(
    "en-US",
    { year: "numeric", month: "long", day: "numeric" },
  );

  return (
    <article className="mt-16 space-y-12">
      <section>
        <h2 className="font-display text-xl font-semibold">
          What is this tool?
        </h2>
        <div className="mt-4 space-y-4 text-base leading-relaxed text-[var(--muted)]">
          {whatIsParagraphs.map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-xl font-semibold">How to use</h2>
        <ol className="mt-4 list-decimal space-y-3 ps-5 text-base leading-relaxed text-[var(--muted)]">
          {guide.howTo.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </section>

      <section>
        <h2 className="font-display text-xl font-semibold">Benefits</h2>
        <ul className="mt-4 list-disc space-y-2 ps-5 text-base leading-relaxed text-[var(--muted)]">
          {guide.benefits.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-xl font-semibold">Use cases</h2>
        <ul className="mt-4 list-disc space-y-2 ps-5 text-base leading-relaxed text-[var(--muted)]">
          {guide.useCases.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="surface rounded-[var(--radius-lg)] p-6">
        <h2 className="font-display text-xl font-semibold">Example</h2>
        <p className="mt-3 text-sm text-[var(--muted)]">
          A practical walkthrough for {name}:
        </p>
        <pre className="mt-4 overflow-x-auto whitespace-pre-wrap rounded-[var(--radius-md)] bg-[color-mix(in_oklab,var(--foreground)_4%,transparent)] p-4 font-mono text-sm leading-relaxed text-[var(--foreground)]">
          {guide.example}
        </pre>
      </section>

      <p className="text-sm text-[var(--muted)]">
        Last updated:{" "}
        <time dateTime={guide.updatedAt}>{updatedLabel}</time>
      </p>
    </article>
  );
}
