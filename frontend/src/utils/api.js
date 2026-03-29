import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000, // 5 min timeout for full pipeline
});

export const analyzeCompany = async (ticker) => {
  const response = await api.post(`/api/analyze/${ticker}`);
  return response.data;
};

export const getCompany = async (ticker) => {
  const response = await api.get(`/api/company/${ticker}`);
  return response.data;
};

export const queryAgent = async (ticker, question) => {
  const response = await api.post("/api/agent/query", { ticker, question });
  return response.data;
};

export const getExportUrl = (ticker, format) => {
  return `${API_BASE}/api/export/${ticker}/${format}`;
};

export default api;
