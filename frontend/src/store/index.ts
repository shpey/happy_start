import { configureStore } from '@reduxjs/toolkit';

// 这里会添加各种slice
export const store = configureStore({
  reducer: {
    // 暂时空白，后续添加reducers
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 