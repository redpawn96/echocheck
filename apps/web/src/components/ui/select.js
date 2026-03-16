import { jsx as _jsx } from "react/jsx-runtime";
import { cn } from "../../lib/cn";
export function Select({ className, ...props }) {
    return (_jsx("select", { className: cn("w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-brandTeal transition focus:ring-2", className), ...props }));
}
