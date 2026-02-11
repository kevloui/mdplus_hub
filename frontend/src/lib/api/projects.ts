import apiClient from "./client";
import type { Project, ProjectDetail } from "@/types/api";

export async function getProjects(limit = 50, offset = 0) {
  const response = await apiClient.get<{ projects: Project[]; total: number }>(
    `/api/v1/projects/`,
    { params: { limit, offset } },
  );
  return response.data;
}

export async function getProject(projectId: string) {
  const response = await apiClient.get<ProjectDetail>(
    `/api/v1/projects/${projectId}`,
  );
  return response.data;
}

export async function createProject(data: { name: string; description?: string }) {
  const response = await apiClient.post<Project>(`/api/v1/projects/`, data);
  return response.data;
}

export async function updateProject(
  projectId: string,
  data: { name?: string; description?: string },
) {
  const response = await apiClient.patch<Project>(
    `/api/v1/projects/${projectId}`,
    data,
  );
  return response.data;
}

export async function deleteProject(projectId: string) {
  await apiClient.delete(`/api/v1/projects/${projectId}`);
}

export async function getTrainedModelsCount() {
  const response = await apiClient.get<{ trained_models_count: number }>(
    `/api/v1/projects/stats/trained-models`,
  );
  return response.data;
}
