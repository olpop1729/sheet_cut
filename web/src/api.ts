import type {
  GenerationDetail,
  GenerationSummary,
  MachineConfigValues,
  MachineConfigVersion,
  PlotSeries,
  Profile,
  RunParameters,
  StepsPage,
  ToolSpec,
} from "./types";

const BASE = "/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body.detail) {
        detail =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      }
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listProfiles: () => request<Profile[]>("/profiles"),
  getProfile: (id: number) => request<Profile>(`/profiles/${id}`),
  createProfile: (name: string, tools: ToolSpec[]) =>
    request<Profile>("/profiles", {
      method: "POST",
      body: JSON.stringify({ name, tools }),
    }),
  updateProfile: (id: number, name: string, tools: ToolSpec[]) =>
    request<Profile>(`/profiles/${id}`, {
      method: "PUT",
      body: JSON.stringify({ name, tools }),
    }),
  deleteProfile: (id: number) =>
    request<void>(`/profiles/${id}`, { method: "DELETE" }),
  generate: (profileId: number, params: RunParameters) =>
    request<GenerationSummary>(`/profiles/${profileId}/generate`, {
      method: "POST",
      body: JSON.stringify(params),
    }),
  listGenerations: () => request<GenerationSummary[]>("/generations"),
  getGeneration: (id: number) => request<GenerationDetail>(`/generations/${id}`),
  getSteps: (id: number, offset: number, limit: number) =>
    request<StepsPage>(`/generations/${id}/steps?offset=${offset}&limit=${limit}`),
  getPlot: (id: number) => request<PlotSeries>(`/generations/${id}/plot`),
  artifactUrl: (id: number) => `${BASE}/generations/${id}/artifact.xlsx`,
  getMachineConfig: () => request<MachineConfigVersion>("/machine-config"),
  updateMachineConfig: (config: MachineConfigValues, comment: string) =>
    request<MachineConfigVersion>("/machine-config", {
      method: "PUT",
      body: JSON.stringify({ ...config, comment }),
    }),
  machineConfigHistory: () =>
    request<MachineConfigVersion[]>("/machine-config/history"),
};
