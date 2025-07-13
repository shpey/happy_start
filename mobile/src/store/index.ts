import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { combineReducers } from '@reduxjs/toolkit';

// 持久化配置
const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['user', 'settings', 'theme'],
};

// 基础 reducer 
const authReducer = (state = { user: null, isAuthenticated: false }, action: any) => {
  switch (action.type) {
    case 'AUTH_LOGIN':
      return { ...state, user: action.payload, isAuthenticated: true };
    case 'AUTH_LOGOUT':
      return { ...state, user: null, isAuthenticated: false };
    default:
      return state;
  }
};

const settingsReducer = (state = { language: 'zh-CN', theme: 'auto' }, action: any) => {
  switch (action.type) {
    case 'SETTINGS_UPDATE':
      return { ...state, ...action.payload };
    default:
      return state;
  }
};

const thinkingReducer = (state = { analyses: [], currentSession: null }, action: any) => {
  switch (action.type) {
    case 'THINKING_ADD_ANALYSIS':
      return { ...state, analyses: [...state.analyses, action.payload] };
    case 'THINKING_SET_SESSION':
      return { ...state, currentSession: action.payload };
    default:
      return state;
  }
};

// 合并 reducers
const rootReducer = combineReducers({
  auth: authReducer,
  settings: settingsReducer,
  thinking: thinkingReducer,
});

// 持久化 reducer
const persistedReducer = persistReducer(persistConfig, rootReducer);

// 配置 store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 