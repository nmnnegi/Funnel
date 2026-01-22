import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { WorkStage } from '../../types';

interface StagesState {
  stages: WorkStage[];
  selectedStage: WorkStage | null;
  loading: boolean;
  error: string | null;
}

const initialState: StagesState = {
  stages: [],
  selectedStage: null,
  loading: false,
  error: null,
};

const stagesSlice = createSlice({
  name: 'stages',
  initialState,
  reducers: {
    setStages: (state, action: PayloadAction<WorkStage[]>) => {
      state.stages = action.payload.sort((a, b) => a.order - b.order);
      state.loading = false;
      state.error = null;
    },
    setSelectedStage: (state, action: PayloadAction<WorkStage | null>) => {
      state.selectedStage = action.payload;
    },
    addStage: (state, action: PayloadAction<WorkStage>) => {
      state.stages.push(action.payload);
      state.stages.sort((a, b) => a.order - b.order);
    },
    updateStage: (state, action: PayloadAction<WorkStage>) => {
      const index = state.stages.findIndex((stage) => stage.uid === action.payload.uid);
      if (index !== -1) {
        state.stages[index] = action.payload;
      }
      if (state.selectedStage?.uid === action.payload.uid) {
        state.selectedStage = action.payload;
      }
      state.stages.sort((a, b) => a.order - b.order);
    },
    removeStage: (state, action: PayloadAction<string>) => {
      state.stages = state.stages.filter((stage) => stage.uid !== action.payload);
      if (state.selectedStage?.uid === action.payload) {
        state.selectedStage = null;
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
  setStages,
  setSelectedStage,
  addStage,
  updateStage,
  removeStage,
  setLoading,
  setError,
} = stagesSlice.actions;

export default stagesSlice.reducer;
