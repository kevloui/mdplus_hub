import apiClient from "./client";
import type { User } from "@/types/api";

export async function getCurrentUser() {
  const response = await apiClient.get<User>(`/api/v1/auth/me`);
  return response.data;
}
