"use client";

import { motion } from "framer-motion";

export function HeroVisual() {
  return (
    <motion.div
      className="relative aspect-[4/3] w-full overflow-hidden rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)]"
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      aria-hidden
    >
      <div className="absolute inset-0 bg-mesh" />
      <motion.div
        className="absolute -start-10 top-10 h-40 w-40 rounded-full bg-[var(--accent)]/30 blur-3xl"
        animate={{ x: [0, 30, 0], y: [0, 20, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute -end-8 bottom-8 h-48 w-48 rounded-full bg-[var(--color-accent-bright)]/25 blur-3xl"
        animate={{ x: [0, -24, 0], y: [0, -16, 0] }}
        transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
      />
      <div className="absolute inset-6 grid grid-cols-6 gap-2 opacity-70">
        {Array.from({ length: 24 }).map((_, i) => (
          <motion.div
            key={i}
            className="rounded-sm border border-[var(--border)] bg-[color-mix(in_oklab,var(--accent)_8%,transparent)]"
            initial={{ opacity: 0.2 }}
            animate={{ opacity: [0.2, 0.7, 0.2] }}
            transition={{
              duration: 2.4,
              delay: (i % 6) * 0.12,
              repeat: Infinity,
            }}
          />
        ))}
      </div>
      <div className="absolute inset-x-8 bottom-8 rounded-[var(--radius-md)] border border-[var(--border)] bg-[color-mix(in_oklab,var(--background)_75%,transparent)] p-4 backdrop-blur">
        <div className="h-2 w-24 rounded-full bg-[var(--accent)]" />
        <div className="mt-3 space-y-2">
          <div className="h-2 w-full rounded-full bg-[var(--border)]" />
          <div className="h-2 w-4/5 rounded-full bg-[var(--border)]" />
          <div className="h-2 w-3/5 rounded-full bg-[var(--border)]" />
        </div>
      </div>
    </motion.div>
  );
}
