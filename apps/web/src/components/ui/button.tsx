import { createElement, type ButtonHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";

const variants = {
  primary:
    "bg-[var(--accent)] text-[var(--accent-fg)] hover:brightness-110 shadow-[var(--shadow-glow)]",
  secondary:
    "surface text-[var(--foreground)] hover:border-[var(--accent)]/50 hover:bg-[color-mix(in_oklab,var(--accent)_8%,var(--card))]",
  ghost:
    "bg-transparent text-[var(--foreground)] hover:bg-[color-mix(in_oklab,var(--foreground)_6%,transparent)]",
  danger: "bg-[var(--color-danger)] text-white hover:brightness-110",
} as const;

const sizes = {
  sm: "h-8 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-12 px-6 text-base",
  icon: "h-10 w-10 p-0",
} as const;

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
  asChild?: boolean;
  children: ReactNode;
}

export function Button({
  className,
  variant = "primary",
  size = "md",
  asChild,
  children,
  ...props
}: ButtonProps) {
  const classes = cn(
    "inline-flex items-center justify-center gap-2 rounded-[var(--radius-md)] font-medium transition focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50",
    variants[variant],
    sizes[size],
    className,
  );

  if (asChild && typeof children === "object" && children !== null && "type" in (children as object)) {
    const child = children as React.ReactElement<{ className?: string }>;
    return createElement(child.type, {
      ...child.props,
      ...props,
      className: cn(classes, child.props.className),
    });
  }

  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}
