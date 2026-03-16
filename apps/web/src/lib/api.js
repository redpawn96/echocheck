const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
async function request(path, init = {}, token) {
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
    return (await response.json());
}
export function register(email, password) {
    return request("/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
    });
}
export function login(email, password) {
    return request("/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
    });
}
export function listWorkspaces(token) {
    return request("/v1/workspaces", {}, token);
}
export function createWorkspace(token, name) {
    return request("/v1/workspaces", {
        method: "POST",
        body: JSON.stringify({ name }),
    }, token);
}
export function listBrands(token, workspaceId) {
    return request(`/v1/brands?workspace_id=${encodeURIComponent(workspaceId)}`, {}, token);
}
export function createBrand(token, workspaceId, name, industry) {
    return request("/v1/brands", {
        method: "POST",
        body: JSON.stringify({ workspaceId, name, industry }),
    }, token);
}
export function createGeoRun(token, workspaceId, brandId, industry) {
    return request("/v1/geo/runs", {
        method: "POST",
        body: JSON.stringify({
            workspaceId,
            brandId,
            industry,
            providers: ["openai", "gemini", "anthropic"],
            intents: ["best tools in category", "top platforms for teams", "recommended products for growth"],
        }),
    }, token);
}
export function getGeoRun(token, runId) {
    return request(`/v1/geo/runs/${encodeURIComponent(runId)}`, {}, token);
}
export function getWeeklyReport(token, brandId) {
    return request(`/v1/reports/weekly?brandId=${encodeURIComponent(brandId)}`, {}, token);
}
