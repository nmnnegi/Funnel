import { configureStore } from '@reduxjs/toolkit';
import leadsReducer from './slices/leadsSlice';
import stagesReducer from './slices/stagesSlice';
import configsReducer from './slices/configsSlice';

export const store = configureStore({
  reducer: {
    leads: leadsReducer,
    stages: stagesReducer,
    configs: configsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
