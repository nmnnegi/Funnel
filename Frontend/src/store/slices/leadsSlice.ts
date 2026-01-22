import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { WorkItem } from '../../types';

interface LeadsState {
  leads: WorkItem[];
  selectedLead: WorkItem | null;
  loading: boolean;
  error: string | null;
}

const initialState: LeadsState = {
  leads: [],
  selectedLead: null,
  loading: false,
  error: null,
};

const leadsSlice = createSlice({
  name: 'leads',
  initialState,
  reducers: {
    setLeads: (state, action: PayloadAction<WorkItem[]>) => {
      state.leads = action.payload;
      state.loading = false;
      state.error = null;
    },
    setSelectedLead: (state, action: PayloadAction<WorkItem | null>) => {
      state.selectedLead = action.payload;
    },
    addLead: (state, action: PayloadAction<WorkItem>) => {
      state.leads.push(action.payload);
    },
    updateLead: (state, action: PayloadAction<WorkItem>) => {
      const index = state.leads.findIndex((lead) => lead.uid === action.payload.uid);
      if (index !== -1) {
        state.leads[index] = action.payload;
      }
      if (state.selectedLead?.uid === action.payload.uid) {
        state.selectedLead = action.payload;
      }
    },
    removeLead: (state, action: PayloadAction<string>) => {
      state.leads = state.leads.filter((lead) => lead.uid !== action.payload);
      if (state.selectedLead?.uid === action.payload) {
        state.selectedLead = null;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const {
  setLeads,
  setSelectedLead,
  addLead,
  updateLead,
  removeLead,
  setLoading,
  setError,
} = leadsSlice.actions;

export default leadsSlice.reducer;
