import apiClient from './api';
import type { WorkStage } from '../types';

export const stagesApi = {
  getAll: async (configUid?: string) => {
    const params = configUid ? { config: configUid } : {};
    const response = await apiClient.get<WorkStage[]>('/stages/', { params });
    return response.data;
  },

  getOne: async (uid: string) => {
    const response = await apiClient.get<WorkStage>(`/stages/${uid}/`);
    return response.data;
  },

  create: async (data: Partial<WorkStage>) => {
    const response = await apiClient.post<WorkStage>('/stages/', data);
    return response.data;
  },

  update: async (uid: string, data: Partial<WorkStage>) => {
    const response = await apiClient.put<WorkStage>(`/stages/${uid}/`, data);
    return response.data;
  },

  delete: async (uid: string) => {
    await apiClient.delete(`/stages/${uid}/`);
  },
};
