import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  type AuthTokenResponse,
  type Brand,
  createBrand,
  createGeoRun,
  createWorkspace,
  getGeoRun,
  getWeeklyReport,
  listBrands,
  listWorkspaces,
  login,
  register,
  type Workspace,
} from "../lib/api";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Select } from "./ui/select";

const TOKEN_KEY = "echocheck_auth_token";

function useStoredToken() {
  const [token, setTokenState] = useState<string>(() => localStorage.getItem(TOKEN_KEY) ?? "");

  const setToken = (nextToken: string) => {
    setTokenState(nextToken);
    if (nextToken) {
      localStorage.setItem(TOKEN_KEY, nextToken);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  };

  return { token, setToken };
}

function AuthPanel({
  onAuthSuccess,
}: {
  onAuthSuccess: (payload: AuthTokenResponse) => void;
}) {
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("TestPass123!");
  const [mode, setMode] = useState<"register" | "login">("register");

  const mutation = useMutation({
    mutationFn: () => (mode === "register" ? register(email, password) : login(email, password)),
    onSuccess: onAuthSuccess,
  });

  return (
    <Card className="relative z-10 border-teal-200 stage-in stage-in-1">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">Sign In</p>
      <CardTitle>Connect your workspace</CardTitle>
      <CardDescription>Use register once, then login for future sessions.</CardDescription>

      <form
        className="contents"
        onSubmit={(event) => {
          event.preventDefault();
          mutation.mutate();
        }}
      >
        <div className="mt-5 grid gap-3">
          <Input
            placeholder="Email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <Input
            placeholder="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>

        <div className="mt-4 flex gap-2">
          <Button
            variant={mode === "register" ? "primary" : "ghost"}
            onClick={() => setMode("register")}
          >
            Register
          </Button>
          <Button
            variant={mode === "login" ? "primary" : "ghost"}
            onClick={() => setMode("login")}
          >
            Login
          </Button>
        </div>

        <Button className="mt-4 w-full" variant="accent" type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Authenticating..." : mode === "register" ? "Create account" : "Sign in"}
        </Button>
      </form>

      {mutation.error ? <p className="mt-3 text-sm text-red-600">{String(mutation.error)}</p> : null}
    </Card>
  );
}

function statusToVariant(status: string | undefined): "neutral" | "success" | "warning" | "danger" {
  if (status === "completed") return "success";
  if (status === "failed") return "danger";
  if (status === "running" || status === "queued") return "warning";
  return "neutral";
}

function KpiCard({ label, value, tone }: { label: string; value: string | number; tone: "teal" | "green" | "rose" }) {
  const toneMap = {
    teal: "border-teal-100 bg-teal-50 text-teal-700",
    green: "border-emerald-100 bg-emerald-50 text-emerald-700",
    rose: "border-rose-100 bg-rose-50 text-rose-700",
  };

  return (
    <article className={`rounded-2xl border p-4 ${toneMap[tone]}`}>
      <p className="text-xs uppercase tracking-[0.16em]">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
    </article>
  );
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
    onSuccess: (workspace: Workspace) => {
      setActiveWorkspaceId(workspace.id);
      void queryClient.invalidateQueries({ queryKey: ["workspaces", token] });
    },
  });

  const createBrandMutation = useMutation({
    mutationFn: () => createBrand(token, activeWorkspaceId, brandName, industry),
    onSuccess: (brand: Brand) => {
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

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_#e6fffb,_#ffffff_40%,_#ffece7_95%)] text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-12 md:py-16">
        <p className="font-display text-sm uppercase tracking-[0.22em] text-brandTeal">EchoCheck</p>
        <h1 className="mt-3 max-w-3xl font-display text-4xl leading-tight md:text-5xl">
          GEO Visibility Control Center
        </h1>
        <p className="mt-3 max-w-3xl text-lg text-slate-600">
          Register, create a brand workspace, run a GEO scan, and read your weekly mention report from live backend data.
        </p>
        <div className="mt-3 flex items-center gap-3 text-sm text-slate-500">
          <span>{authSummary}</span>
          {latestRunId ? <Badge variant={runBadgeVariant}>{runStatus ?? "queued"}</Badge> : null}
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          {!token ? (
            <AuthPanel
              onAuthSuccess={(payload) => {
                setToken(payload.accessToken);
              }}
            />
          ) : (
            <Card className="border-teal-200 stage-in stage-in-1">
              <CardHeader>
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">Setup</p>
                  <CardTitle>Workspace and brand</CardTitle>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setToken("");
                    setActiveWorkspaceId("");
                    setActiveBrandId("");
                    setLatestRunId("");
                    void queryClient.clear();
                  }}
                >
                  Sign out
                </Button>
              </CardHeader>

              <div className="mt-5 grid gap-3">
                <Input
                  value={workspaceName}
                  onChange={(event) => setWorkspaceName(event.target.value)}
                  placeholder="Workspace name"
                />
                <Button onClick={() => createWorkspaceMutation.mutate()} disabled={createWorkspaceMutation.isPending || !workspaceName.trim()}>
                  {createWorkspaceMutation.isPending ? "Creating..." : "Create workspace"}
                </Button>
              </div>

              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Workspace</p>
                <Select
                  className="mt-2"
                  value={activeWorkspaceId}
                  onChange={(event) => {
                    setActiveWorkspaceId(event.target.value);
                    setActiveBrandId("");
                  }}
                >
                  <option value="">Select workspace</option>
                  {(workspacesQuery.data ?? []).map((workspace) => (
                    <option key={workspace.id} value={workspace.id}>
                      {workspace.name}
                    </option>
                  ))}
                </Select>
              </div>

              <div className="mt-4 grid gap-3">
                <Input
                  value={brandName}
                  onChange={(event) => setBrandName(event.target.value)}
                  placeholder="Brand name"
                />
                <Input
                  value={industry}
                  onChange={(event) => setIndustry(event.target.value)}
                  placeholder="Industry"
                />
                <Button
                  variant="accent"
                  onClick={() => createBrandMutation.mutate()}
                  disabled={createBrandMutation.isPending || !activeWorkspaceId || !brandName.trim() || !industry.trim()}
                >
                  {createBrandMutation.isPending ? "Creating..." : "Create brand"}
                </Button>
              </div>

              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Brand</p>
                <Select
                  className="mt-2"
                  value={activeBrandId}
                  onChange={(event) => setActiveBrandId(event.target.value)}
                >
                  <option value="">Select brand</option>
                  {(brandsQuery.data ?? []).map((brand) => (
                    <option key={brand.id} value={brand.id}>
                      {brand.name} ({brand.industry})
                    </option>
                  ))}
                </Select>
              </div>

              <Button
                className="mt-4 w-full"
                variant="secondary"
                onClick={() => runMutation.mutate()}
                disabled={runMutation.isPending || !activeWorkspaceId || !activeBrandId}
              >
                {runMutation.isPending ? "Queueing run..." : "Run GEO visibility check"}
              </Button>

              {latestRunId ? (
                <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
                  <p className="truncate">Last run: {latestRunId}</p>
                  <p className="mt-1">State: {runStatusQuery.data?.status ?? "queued"}</p>
                </div>
              ) : null}
            </Card>
          )}

          <Card className="border-cyan-200 stage-in stage-in-2">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-700">Weekly Report</p>
            <CardTitle>AI Share of Voice Snapshot</CardTitle>

            {!token || !activeBrandId ? (
              <p className="mt-4 text-sm text-slate-600">Create and select a brand to view report metrics.</p>
            ) : reportQuery.isLoading ? (
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div className="h-24 animate-pulse rounded-2xl bg-slate-100" />
                <div className="h-24 animate-pulse rounded-2xl bg-slate-100" />
                <div className="h-24 animate-pulse rounded-2xl bg-slate-100" />
              </div>
            ) : reportQuery.error ? (
              <p className="mt-4 text-sm text-red-600">{String(reportQuery.error)}</p>
            ) : reportQuery.data ? (
              <div className="mt-6 grid gap-4">
                <div className="grid gap-3 sm:grid-cols-3">
                  <KpiCard label="Mention Rate" value={`${Math.round(reportQuery.data.mentionRate * 100)}%`} tone="teal" />
                  <KpiCard label="Positive" value={reportQuery.data.sentiment.positive} tone="green" />
                  <KpiCard label="Negative" value={reportQuery.data.sentiment.negative} tone="rose" />
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm font-semibold text-slate-700">Provider Breakdown</p>
                  <div className="mt-3 space-y-3">
                    {reportQuery.data.providers.map((provider) => (
                      <div key={provider.name}>
                        <div className="mb-1 flex items-center justify-between text-xs text-slate-600">
                          <span className="uppercase tracking-[0.14em]">{provider.name}</span>
                          <span>{Math.round(provider.mentionRate * 100)}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-slate-200">
                          <div
                            className="h-2 rounded-full bg-gradient-to-r from-teal-500 to-cyan-500"
                            style={{ width: `${Math.max(4, Math.round(provider.mentionRate * 100))}%` }}
                          />
                        </div>
                      </div>
                    ))}
                    {reportQuery.data.providers.length === 0 ? (
                      <p className="text-sm text-slate-500">No provider rows yet. Run a GEO check first.</p>
                    ) : null}
                  </div>
                </div>
              </div>
            ) : null}
          </Card>
        </div>
      </section>
    </main>
  );
}
