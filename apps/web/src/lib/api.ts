export type AuthTokenResponse = {
  accessToken: string;
  tokenType: string;
  user: { id: string; email: string };
};

export type Workspace = {
  id: string;
  name: string;
  createdAt: string;
};

export type Brand = {
  id: string;
  workspaceId: string;
  name: string;
  industry: string;
  createdAt: string;
};

export type GeoRun = {
  runId: string;
  status: string;
};

export type GeoRunStatus = {
  runId: string;
  status: string;
  startedAt: string | null;
  finishedAt: string | null;
};

export type WeeklyReport = {
  brandId: string;
  mentionRate: number;
  sentiment: {
    positive: number;
    neutral: number;
    negative: number;
  };
  providers: Array<{
    name: string;
    mentionRate: number;
  }>;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(init.headers ?? {});
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API ${response.status}: ${body || response.statusText}`);
  }

  return (await response.json()) as T;
}

export function register(email: string, password: string): Promise<AuthTokenResponse> {
  return request<AuthTokenResponse>("/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function login(email: string, password: string): Promise<AuthTokenResponse> {
  return request<AuthTokenResponse>("/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function listWorkspaces(token: string): Promise<Workspace[]> {
  return request<Workspace[]>("/v1/workspaces", {}, token);
}

export function createWorkspace(token: string, name: string): Promise<Workspace> {
  return request<Workspace>(
    "/v1/workspaces",
    {
      method: "POST",
      body: JSON.stringify({ name }),
    },
    token,
  );
}

export function listBrands(token: string, workspaceId: string): Promise<Brand[]> {
  return request<Brand[]>(`/v1/brands?workspace_id=${encodeURIComponent(workspaceId)}`, {}, token);
}

export function createBrand(token: string, workspaceId: string, name: string, industry: string): Promise<Brand> {
  return request<Brand>(
    "/v1/brands",
    {
      method: "POST",
      body: JSON.stringify({ workspaceId, name, industry }),
    },
    token,
  );
}

export function createGeoRun(token: string, workspaceId: string, brandId: string, industry: string): Promise<GeoRun> {
  return request<GeoRun>(
    "/v1/geo/runs",
    {
      method: "POST",
      body: JSON.stringify({
        workspaceId,
        brandId,
        industry,
        providers: ["openai", "gemini", "anthropic"],
        intents: ["best tools in category", "top platforms for teams", "recommended products for growth"],
      }),
    },
    token,
  );
}

export function getGeoRun(token: string, runId: string): Promise<GeoRunStatus> {
  return request<GeoRunStatus>(`/v1/geo/runs/${encodeURIComponent(runId)}`, {}, token);
}

export function getWeeklyReport(token: string, brandId: string): Promise<WeeklyReport> {
  return request<WeeklyReport>(`/v1/reports/weekly?brandId=${encodeURIComponent(brandId)}`, {}, token);
}
