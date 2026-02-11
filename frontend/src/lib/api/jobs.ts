import apiClient from "./client";
import type { Job, Molecule } from "@/types/api";

export async function getJobs(options?: {
  projectId?: string;
  status?: string;
  limit?: number;
  offset?: number;
}) {
  const params: Record<string, string | number> = {};
  if (options?.projectId) params.project_id = options.projectId;
  if (options?.status) params.status = options.status;
  if (options?.limit) params.limit = options.limit;
  if (options?.offset) params.offset = options.offset;

  const response = await apiClient.get<{ jobs: Job[]; total: number }>(
    `/api/v1/jobs/`,
    { params },
  );
  return response.data;
}

export async function getJob(jobId: string) {
  const response = await apiClient.get<Job>(`/api/v1/jobs/${jobId}`);
  return response.data;
}

export async function cancelJob(jobId: string) {
  await apiClient.delete(`/api/v1/jobs/${jobId}`);
}

export async function downloadJobResult(jobId: string) {
  const response = await apiClient.get(`/api/v1/jobs/${jobId}/download`, {
    responseType: "blob",
  });
  const blob = new Blob([response.data]);
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `inference_result_${jobId}.npy`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export async function createMoleculeFromJob(jobId: string, name?: string) {
  const params = name ? { name } : {};
  const response = await apiClient.post<Molecule>(
    `/api/v1/jobs/${jobId}/create-molecule`,
    null,
    { params },
  );
  return response.data;
}
