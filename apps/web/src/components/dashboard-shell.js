import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createBrand, createGeoRun, createWorkspace, getGeoRun, getWeeklyReport, listBrands, listWorkspaces, login, register, } from "../lib/api";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Select } from "./ui/select";
const TOKEN_KEY = "echocheck_auth_token";
function useStoredToken() {
    const [token, setTokenState] = useState(() => localStorage.getItem(TOKEN_KEY) ?? "");
    const setToken = (nextToken) => {
        setTokenState(nextToken);
        if (nextToken) {
            localStorage.setItem(TOKEN_KEY, nextToken);
        }
        else {
            localStorage.removeItem(TOKEN_KEY);
        }
    };
    return { token, setToken };
}
function AuthPanel({ onAuthSuccess, }) {
    const [email, setEmail] = useState("demo@example.com");
    const [password, setPassword] = useState("TestPass123!");
    const [mode, setMode] = useState("register");
    const mutation = useMutation({
        mutationFn: () => (mode === "register" ? register(email, password) : login(email, password)),
        onSuccess: onAuthSuccess,
    });
    return (_jsxs(Card, { className: "relative z-10 border-teal-200 stage-in stage-in-1", children: [_jsx("p", { className: "text-sm font-semibold uppercase tracking-[0.18em] text-teal-700", children: "Sign In" }), _jsx(CardTitle, { children: "Connect your workspace" }), _jsx(CardDescription, { children: "Use register once, then login for future sessions." }), _jsxs("form", { className: "contents", onSubmit: (event) => {
                    event.preventDefault();
                    mutation.mutate();
                }, children: [_jsxs("div", { className: "mt-5 grid gap-3", children: [_jsx(Input, { placeholder: "Email", value: email, onChange: (event) => setEmail(event.target.value) }), _jsx(Input, { placeholder: "Password", type: "password", value: password, onChange: (event) => setPassword(event.target.value) })] }), _jsxs("div", { className: "mt-4 flex gap-2", children: [_jsx(Button, { variant: mode === "register" ? "primary" : "ghost", onClick: () => setMode("register"), children: "Register" }), _jsx(Button, { variant: mode === "login" ? "primary" : "ghost", onClick: () => setMode("login"), children: "Login" })] }), _jsx(Button, { className: "mt-4 w-full", variant: "accent", type: "submit", disabled: mutation.isPending, children: mutation.isPending ? "Authenticating..." : mode === "register" ? "Create account" : "Sign in" })] }), mutation.error ? _jsx("p", { className: "mt-3 text-sm text-red-600", children: String(mutation.error) }) : null] }));
}
function statusToVariant(status) {
    if (status === "completed")
        return "success";
    if (status === "failed")
        return "danger";
    if (status === "running" || status === "queued")
        return "warning";
    return "neutral";
}
function KpiCard({ label, value, tone }) {
    const toneMap = {
        teal: "border-teal-100 bg-teal-50 text-teal-700",
        green: "border-emerald-100 bg-emerald-50 text-emerald-700",
        rose: "border-rose-100 bg-rose-50 text-rose-700",
    };
    return (_jsxs("article", { className: `rounded-2xl border p-4 ${toneMap[tone]}`, children: [_jsx("p", { className: "text-xs uppercase tracking-[0.16em]", children: label }), _jsx("p", { className: "mt-2 text-3xl font-semibold text-slate-900", children: value })] }));
}
export function DashboardShell() {
    const queryClient = useQueryClient();
    const { token, setToken } = useStoredToken();
    const [workspaceName, setWorkspaceName] = useState("Growth Team Workspace");
    const [brandName, setBrandName] = useState("EchoCheck");
    const [industry, setIndustry] = useState("MarTech");
    const [activeWorkspaceId, setActiveWorkspaceId] = useState("");
    const [activeBrandId, setActiveBrandId] = useState("");
    const [latestRunId, setLatestRunId] = useState("");
    const workspacesQuery = useQuery({
        queryKey: ["workspaces", token],
        queryFn: () => listWorkspaces(token),
        enabled: Boolean(token),
    });
    useEffect(() => {
        if (!activeWorkspaceId && workspacesQuery.data && workspacesQuery.data.length > 0) {
            setActiveWorkspaceId(workspacesQuery.data[0].id);
        }
    }, [activeWorkspaceId, workspacesQuery.data]);
    const brandsQuery = useQuery({
        queryKey: ["brands", token, activeWorkspaceId],
        queryFn: () => listBrands(token, activeWorkspaceId),
        enabled: Boolean(token && activeWorkspaceId),
    });
    useEffect(() => {
        if (!activeBrandId && brandsQuery.data && brandsQuery.data.length > 0) {
            setActiveBrandId(brandsQuery.data[0].id);
        }
    }, [activeBrandId, brandsQuery.data]);
    const createWorkspaceMutation = useMutation({
        mutationFn: () => createWorkspace(token, workspaceName),
        onSuccess: (workspace) => {
            setActiveWorkspaceId(workspace.id);
            void queryClient.invalidateQueries({ queryKey: ["workspaces", token] });
        },
    });
    const createBrandMutation = useMutation({
        mutationFn: () => createBrand(token, activeWorkspaceId, brandName, industry),
        onSuccess: (brand) => {
            setActiveBrandId(brand.id);
            void queryClient.invalidateQueries({ queryKey: ["brands", token, activeWorkspaceId] });
        },
    });
    const runMutation = useMutation({
        mutationFn: () => createGeoRun(token, activeWorkspaceId, activeBrandId, industry),
        onSuccess: (payload) => {
            setLatestRunId(payload.runId);
            void queryClient.invalidateQueries({ queryKey: ["geo-run", token, payload.runId] });
            void queryClient.invalidateQueries({ queryKey: ["weekly-report", token, activeBrandId] });
        },
    });
    const runStatusQuery = useQuery({
        queryKey: ["geo-run", token, latestRunId],
        queryFn: () => getGeoRun(token, latestRunId),
        enabled: Boolean(token && latestRunId),
        refetchInterval: (query) => {
            const status = query.state.data?.status;
            return status === "completed" || status === "failed" ? false : 1200;
        },
    });
    const reportQuery = useQuery({
        queryKey: ["weekly-report", token, activeBrandId],
        queryFn: () => getWeeklyReport(token, activeBrandId),
        enabled: Boolean(token && activeBrandId),
    });
    const authSummary = useMemo(() => {
        if (!token) {
            return "Not authenticated";
        }
        return `Authenticated (${token.slice(0, 8)}...)`;
    }, [token]);
    const runStatus = runStatusQuery.data?.status;
    const runBadgeVariant = statusToVariant(runStatus);
    return (_jsx("main", { className: "min-h-screen bg-[radial-gradient(circle_at_top,_#e6fffb,_#ffffff_40%,_#ffece7_95%)] text-slate-900", children: _jsxs("section", { className: "mx-auto max-w-6xl px-6 py-12 md:py-16", children: [_jsx("p", { className: "font-display text-sm uppercase tracking-[0.22em] text-brandTeal", children: "EchoCheck" }), _jsx("h1", { className: "mt-3 max-w-3xl font-display text-4xl leading-tight md:text-5xl", children: "GEO Visibility Control Center" }), _jsx("p", { className: "mt-3 max-w-3xl text-lg text-slate-600", children: "Register, create a brand workspace, run a GEO scan, and read your weekly mention report from live backend data." }), _jsxs("div", { className: "mt-3 flex items-center gap-3 text-sm text-slate-500", children: [_jsx("span", { children: authSummary }), latestRunId ? _jsx(Badge, { variant: runBadgeVariant, children: runStatus ?? "queued" }) : null] }), _jsxs("div", { className: "mt-8 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]", children: [!token ? (_jsx(AuthPanel, { onAuthSuccess: (payload) => {
                                setToken(payload.accessToken);
                            } })) : (_jsxs(Card, { className: "border-teal-200 stage-in stage-in-1", children: [_jsxs(CardHeader, { children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm font-semibold uppercase tracking-[0.18em] text-teal-700", children: "Setup" }), _jsx(CardTitle, { children: "Workspace and brand" })] }), _jsx(Button, { variant: "ghost", size: "sm", onClick: () => {
                                                setToken("");
                                                setActiveWorkspaceId("");
                                                setActiveBrandId("");
                                                setLatestRunId("");
                                                void queryClient.clear();
                                            }, children: "Sign out" })] }), _jsxs("div", { className: "mt-5 grid gap-3", children: [_jsx(Input, { value: workspaceName, onChange: (event) => setWorkspaceName(event.target.value), placeholder: "Workspace name" }), _jsx(Button, { onClick: () => createWorkspaceMutation.mutate(), disabled: createWorkspaceMutation.isPending || !workspaceName.trim(), children: createWorkspaceMutation.isPending ? "Creating..." : "Create workspace" })] }), _jsxs("div", { className: "mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3", children: [_jsx("p", { className: "text-xs uppercase tracking-[0.16em] text-slate-500", children: "Workspace" }), _jsxs(Select, { className: "mt-2", value: activeWorkspaceId, onChange: (event) => {
                                                setActiveWorkspaceId(event.target.value);
                                                setActiveBrandId("");
                                            }, children: [_jsx("option", { value: "", children: "Select workspace" }), (workspacesQuery.data ?? []).map((workspace) => (_jsx("option", { value: workspace.id, children: workspace.name }, workspace.id)))] })] }), _jsxs("div", { className: "mt-4 grid gap-3", children: [_jsx(Input, { value: brandName, onChange: (event) => setBrandName(event.target.value), placeholder: "Brand name" }), _jsx(Input, { value: industry, onChange: (event) => setIndustry(event.target.value), placeholder: "Industry" }), _jsx(Button, { variant: "accent", onClick: () => createBrandMutation.mutate(), disabled: createBrandMutation.isPending || !activeWorkspaceId || !brandName.trim() || !industry.trim(), children: createBrandMutation.isPending ? "Creating..." : "Create brand" })] }), _jsxs("div", { className: "mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3", children: [_jsx("p", { className: "text-xs uppercase tracking-[0.16em] text-slate-500", children: "Brand" }), _jsxs(Select, { className: "mt-2", value: activeBrandId, onChange: (event) => setActiveBrandId(event.target.value), children: [_jsx("option", { value: "", children: "Select brand" }), (brandsQuery.data ?? []).map((brand) => (_jsxs("option", { value: brand.id, children: [brand.name, " (", brand.industry, ")"] }, brand.id)))] })] }), _jsx(Button, { className: "mt-4 w-full", variant: "secondary", onClick: () => runMutation.mutate(), disabled: runMutation.isPending || !activeWorkspaceId || !activeBrandId, children: runMutation.isPending ? "Queueing run..." : "Run GEO visibility check" }), latestRunId ? (_jsxs("div", { className: "mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600", children: [_jsxs("p", { className: "truncate", children: ["Last run: ", latestRunId] }), _jsxs("p", { className: "mt-1", children: ["State: ", runStatusQuery.data?.status ?? "queued"] })] })) : null] })), _jsxs(Card, { className: "border-cyan-200 stage-in stage-in-2", children: [_jsx("p", { className: "text-sm font-semibold uppercase tracking-[0.18em] text-cyan-700", children: "Weekly Report" }), _jsx(CardTitle, { children: "AI Share of Voice Snapshot" }), !token || !activeBrandId ? (_jsx("p", { className: "mt-4 text-sm text-slate-600", children: "Create and select a brand to view report metrics." })) : reportQuery.isLoading ? (_jsxs("div", { className: "mt-4 grid gap-3 sm:grid-cols-3", children: [_jsx("div", { className: "h-24 animate-pulse rounded-2xl bg-slate-100" }), _jsx("div", { className: "h-24 animate-pulse rounded-2xl bg-slate-100" }), _jsx("div", { className: "h-24 animate-pulse rounded-2xl bg-slate-100" })] })) : reportQuery.error ? (_jsx("p", { className: "mt-4 text-sm text-red-600", children: String(reportQuery.error) })) : reportQuery.data ? (_jsxs("div", { className: "mt-6 grid gap-4", children: [_jsxs("div", { className: "grid gap-3 sm:grid-cols-3", children: [_jsx(KpiCard, { label: "Mention Rate", value: `${Math.round(reportQuery.data.mentionRate * 100)}%`, tone: "teal" }), _jsx(KpiCard, { label: "Positive", value: reportQuery.data.sentiment.positive, tone: "green" }), _jsx(KpiCard, { label: "Negative", value: reportQuery.data.sentiment.negative, tone: "rose" })] }), _jsxs("div", { className: "rounded-2xl border border-slate-200 bg-slate-50 p-4", children: [_jsx("p", { className: "text-sm font-semibold text-slate-700", children: "Provider Breakdown" }), _jsxs("div", { className: "mt-3 space-y-3", children: [reportQuery.data.providers.map((provider) => (_jsxs("div", { children: [_jsxs("div", { className: "mb-1 flex items-center justify-between text-xs text-slate-600", children: [_jsx("span", { className: "uppercase tracking-[0.14em]", children: provider.name }), _jsxs("span", { children: [Math.round(provider.mentionRate * 100), "%"] })] }), _jsx("div", { className: "h-2 rounded-full bg-slate-200", children: _jsx("div", { className: "h-2 rounded-full bg-gradient-to-r from-teal-500 to-cyan-500", style: { width: `${Math.max(4, Math.round(provider.mentionRate * 100))}%` } }) })] }, provider.name))), reportQuery.data.providers.length === 0 ? (_jsx("p", { className: "text-sm text-slate-500", children: "No provider rows yet. Run a GEO check first." })) : null] })] })] })) : null] })] })] }) }));
}
