import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Card({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  return (
    <div
      className={cn(
        "surface rounded-[var(--radius-lg)] p-5 shadow-sm",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
