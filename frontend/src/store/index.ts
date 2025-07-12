import { configureStore, createSlice } from '@reduxjs/toolkit';

// 创建一个基本的应用状态slice
const appSlice = createSlice({
  name: 'app',
  initialState: {
    isLoading: false,
    error: null as string | null,
    theme: 'light',
  },
  reducers: {
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    setTheme: (state, action) => {
      state.theme = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

// 导出actions
export const { setLoading, setError, setTheme, clearError } = appSlice.actions;

// 配置store
export const store = configureStore({
  reducer: {
    app: appSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 