import apiClient from "./client";
import type { Molecule } from "@/types/api";

export async function getMolecules(projectId: string, limit = 50, offset = 0) {
  const response = await apiClient.get<{ molecules: Molecule[]; total: number }>(
    `/api/v1/molecules/`,
    { params: { project_id: projectId, limit, offset } },
  );
  return response.data;
}

export async function getMolecule(moleculeId: string) {
  const response = await apiClient.get<Molecule>(
    `/api/v1/molecules/${moleculeId}`,
  );
  return response.data;
}

export async function getMoleculeStructure(moleculeId: string) {
  const response = await apiClient.get<{
    id: string;
    name: string;
    format: string;
    content: string;
  }>(`/api/v1/molecules/${moleculeId}/structure`);
  return response.data;
}

export async function uploadMolecule(
  projectId: string,
  file: File,
  options?: {
    name?: string;
    description?: string;
    moleculeType?: "coarse_grained" | "atomistic" | "backmapped";
  },
) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("project_id", projectId);
  if (options?.name) formData.append("name", options.name);
  if (options?.description) formData.append("description", options.description);
  if (options?.moleculeType) formData.append("molecule_type", options.moleculeType);

  const response = await apiClient.post<Molecule>(`/api/v1/molecules/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function deleteMolecule(moleculeId: string) {
  await apiClient.delete(`/api/v1/molecules/${moleculeId}`);
}
