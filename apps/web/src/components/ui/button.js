import { jsx as _jsx } from "react/jsx-runtime";
import { cn } from "../../lib/cn";
const variantClassMap = {
    primary: "bg-brandTeal text-white hover:bg-teal-700",
    secondary: "bg-slate-900 text-white hover:bg-slate-800",
    ghost: "bg-slate-100 text-slate-700 hover:bg-slate-200",
    accent: "bg-brandCoral text-white hover:bg-orange-600",
    danger: "bg-rose-600 text-white hover:bg-rose-700",
};
const sizeClassMap = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-5 py-2.5 text-base",
};
export function Button({ className, variant = "primary", size = "md", type = "button", ...props }) {
    return (_jsx("button", { type: type, className: cn("pointer-events-auto inline-flex cursor-pointer items-center justify-center rounded-xl font-semibold transition disabled:cursor-not-allowed disabled:opacity-60", variantClassMap[variant], sizeClassMap[size], className), ...props }));
}
