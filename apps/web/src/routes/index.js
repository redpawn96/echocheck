import { createRoute } from "@tanstack/react-router";
import { rootRoute } from "./__root";
import { DashboardShell } from "../components/dashboard-shell";
export const indexRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/",
    component: DashboardShell,
});
