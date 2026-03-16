import type { InputHTMLAttributes } from "react";

import { cn } from "../../lib/cn";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-brandTeal transition placeholder:text-slate-400 focus:ring-2",
        className,
      )}
      {...props}
    />
  );
}
