import { jsx as _jsx } from "react/jsx-runtime";
import { cn } from "../../lib/cn";
export function Card({ className, ...props }) {
    return _jsx("section", { className: cn("rounded-3xl border bg-white/90 p-6 shadow-lg", className), ...props });
}
export function CardHeader({ className, ...props }) {
    return _jsx("div", { className: cn("flex items-start justify-between gap-4", className), ...props });
}
export function CardTitle({ className, ...props }) {
    return _jsx("h2", { className: cn("mt-2 font-display text-2xl", className), ...props });
}
export function CardDescription({ className, ...props }) {
    return _jsx("p", { className: cn("mt-2 text-sm text-slate-600", className), ...props });
}
