import { jsx as _jsx } from "react/jsx-runtime";
import { cn } from "../../lib/cn";
const variantClassMap = {
    neutral: "bg-slate-100 text-slate-700",
    success: "bg-emerald-100 text-emerald-700",
    warning: "bg-amber-100 text-amber-700",
    danger: "bg-rose-100 text-rose-700",
};
export function Badge({ className, children, variant = "neutral", ...props }) {
    return (_jsx("span", { className: cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.08em]", variantClassMap[variant], className), ...props, children: children }));
}
