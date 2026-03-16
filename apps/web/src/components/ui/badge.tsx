import type { HTMLAttributes } from "react";

import { cn } from "../../lib/cn";

type BadgeVariant = "neutral" | "success" | "warning" | "danger";
type BadgeProps = HTMLAttributes<HTMLSpanElement> & { variant?: BadgeVariant };

const variantClassMap: Record<BadgeVariant, string> = {
  neutral: "bg-slate-100 text-slate-700",
  success: "bg-emerald-100 text-emerald-700",
  warning: "bg-amber-100 text-amber-700",
  danger: "bg-rose-100 text-rose-700",
};

export function Badge({ className, children, variant = "neutral", ...props }: BadgeProps) {

  return (
    <span
      className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.08em]", variantClassMap[variant], className)}
      {...props}
    >
      {children}
    </span>
  );
}
