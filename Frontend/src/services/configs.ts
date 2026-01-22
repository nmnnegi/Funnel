import apiClient from './api';
import type { WorkItemConfig } from '../types';

export const configsApi = {
  getAll: async () => {
    const response = await apiClient.get<WorkItemConfig[]>('/config/');
    return response.data;
  },

  getOne: async (uid: string) => {
    const response = await apiClient.get<WorkItemConfig>(`/config/${uid}/`);
    return response.data;
  },

  create: async (data: Partial<WorkItemConfig>) => {
    const response = await apiClient.post<WorkItemConfig>('/config/', data);
    return response.data;
  },

  update: async (uid: string, data: Partial<WorkItemConfig>) => {
    const response = await apiClient.put<WorkItemConfig>(`/config/${uid}/`, data);
    return response.data;
  },

  delete: async (uid: string) => {
    await apiClient.delete(`/config/${uid}/`);
  },
};
