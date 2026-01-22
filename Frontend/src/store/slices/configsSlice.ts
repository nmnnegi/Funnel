import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { WorkItemConfig } from '../../types';

interface ConfigsState {
  configs: WorkItemConfig[];
  selectedConfig: WorkItemConfig | null;
  loading: boolean;
  error: string | null;
}

const initialState: ConfigsState = {
  configs: [],
  selectedConfig: null,
  loading: false,
  error: null,
};

const configsSlice = createSlice({
  name: 'configs',
  initialState,
  reducers: {
    setConfigs: (state, action: PayloadAction<WorkItemConfig[]>) => {
      state.configs = action.payload;
      state.loading = false;
      state.error = null;
      // Auto-select first config if none selected
      if (!state.selectedConfig && action.payload.length > 0) {
        state.selectedConfig = action.payload[0];
      }
    },
    setSelectedConfig: (state, action: PayloadAction<WorkItemConfig | null>) => {
      state.selectedConfig = action.payload;
    },
    addConfig: (state, action: PayloadAction<WorkItemConfig>) => {
      state.configs.push(action.payload);
    },
    updateConfig: (state, action: PayloadAction<WorkItemConfig>) => {
      const index = state.configs.findIndex((cfg) => cfg.uid === action.payload.uid);
      if (index !== -1) {
        state.configs[index] = action.payload;
      }
      if (state.selectedConfig?.uid === action.payload.uid) {
        state.selectedConfig = action.payload;
      }
    },
    removeConfig: (state, action: PayloadAction<string>) => {
      state.configs = state.configs.filter((cfg) => cfg.uid !== action.payload);
      if (state.selectedConfig?.uid === action.payload) {
        state.selectedConfig = state.configs[0] || null;
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
  setConfigs,
  setSelectedConfig,
  addConfig,
  updateConfig,
  removeConfig,
  setLoading,
  setError,
} = configsSlice.actions;

export default configsSlice.reducer;
