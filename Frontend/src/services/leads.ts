import apiClient from './api';
import type { WorkItem } from '../types';

export const leadsApi = {
  getAll: async (configUid?: string, stage?: string) => {
    const params: any = { limit: 1000 };
    if (configUid) params.config = configUid;
    if (stage) params.current_stage = stage;
    const response = await apiClient.get<{ results: WorkItem[]; count: number }>('/leads/', { params });
    return response.data.results;
  },

  getOne: async (uid: string) => {
    const response = await apiClient.get<WorkItem>(`/leads/${uid}/`);
    return response.data;
  },

  create: async (data: Partial<WorkItem>) => {
    const response = await apiClient.post<WorkItem>('/leads/', data);
    return response.data;
  },

  update: async (uid: string, data: Partial<WorkItem>) => {
    const response = await apiClient.put<WorkItem>(`/leads/${uid}/`, data);
    return response.data;
  },

  moveStage: async (uid: string, targetStage: string) => {
    const response = await apiClient.patch<WorkItem>(`/leads/${uid}/move-stage/`, {
      target_stage: targetStage,
    });
    return response.data;
  },

  delete: async (uid: string) => {
    await apiClient.delete(`/leads/${uid}/`);
  },
};
