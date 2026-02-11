import apiClient from "./client";
import type { GlimpsModel } from "@/types/api";

export async function getModels(projectId: string, limit = 50, offset = 0) {
  const response = await apiClient.get<{ models: GlimpsModel[]; total: number }>(
    `/api/v1/models/`,
    { params: { project_id: projectId, limit, offset } },
  );
  return response.data;
}

export async function getModel(modelId: string) {
  const response = await apiClient.get<GlimpsModel>(
    `/api/v1/models/${modelId}`,
  );
  return response.data;
}

export async function createModel(data: {
  project_id: string;
  name: string;
  description?: string;
}) {
  const response = await apiClient.post<GlimpsModel>(`/api/v1/models/`, data);
  return response.data;
}

export interface GlimpsOptions {
  pca: boolean;
  refine: boolean;
  shave: boolean;
  triangulate: boolean;
}

export const DEFAULT_GLIMPS_OPTIONS: GlimpsOptions = {
  pca: false,
  refine: true,
  shave: true,
  triangulate: false,
};

export async function trainModel(
  modelId: string,
  cgMoleculeId: string,
  atomisticMoleculeId: string,
  glimpsOptions: GlimpsOptions = DEFAULT_GLIMPS_OPTIONS,
) {
  const formData = new FormData();
  formData.append("cg_molecule_id", cgMoleculeId);
  formData.append("atomistic_molecule_id", atomisticMoleculeId);
  formData.append("pca", String(glimpsOptions.pca));
  formData.append("refine", String(glimpsOptions.refine));
  formData.append("shave", String(glimpsOptions.shave));
  formData.append("triangulate", String(glimpsOptions.triangulate));

  const response = await apiClient.post<{
    job_id: string;
    model_id: string;
    status: string;
  }>(`/api/v1/models/${modelId}/train`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function runInference(modelId: string, inputMoleculeId: string) {
  const formData = new FormData();
  formData.append("input_molecule_id", inputMoleculeId);

  const response = await apiClient.post<{
    job_id: string;
    model_id: string;
    status: string;
  }>(`/api/v1/models/${modelId}/inference`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function deleteModel(modelId: string) {
  await apiClient.delete(`/api/v1/models/${modelId}`);
}
