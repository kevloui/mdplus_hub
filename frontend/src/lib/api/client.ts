import axios from "axios";
import { getSession } from "next-auth/react";

let cachedToken: string | null = null;
let tokenExpiry: number | null = null;

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(async (config) => {
  const now = Date.now();

  if (!cachedToken || (tokenExpiry && now >= tokenExpiry - 30000)) {
    const session = await getSession();
    if (session?.accessToken) {
      cachedToken = session.accessToken;
      tokenExpiry = now + 15 * 60 * 1000;
    }
  }

  if (cachedToken) {
    config.headers.Authorization = `Bearer ${cachedToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      cachedToken = null;
      tokenExpiry = null;
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export const clearAuthCache = () => {
  cachedToken = null;
  tokenExpiry = null;
};

export default apiClient;
