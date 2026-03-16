import { jsx as _jsx } from "react/jsx-runtime";
import { createRootRoute, Outlet } from "@tanstack/react-router";
export const rootRoute = createRootRoute({
    component: () => _jsx(Outlet, {}),
});
