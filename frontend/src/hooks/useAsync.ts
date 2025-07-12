/**
 * 异步操作Hook
 * 统一处理加载状态、错误状态和数据状态
 */

import { useState, useEffect, useCallback } from 'react';

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

interface UseAsyncOptions {
  immediate?: boolean;
}

export function useAsync<T>(
  asyncFunction: () => Promise<T>,
  dependencies: any[] = [],
  options: UseAsyncOptions = { immediate: true }
) {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: false,
    error: null
  });

  const execute = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const data = await asyncFunction();
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      setState({ data: null, loading: false, error: error as Error });
      throw error;
    }
  }, dependencies);

  useEffect(() => {
    if (options.immediate) {
      execute();
    }
  }, [execute, options.immediate]);

  return {
    ...state,
    execute,
    reset: useCallback(() => {
      setState({ data: null, loading: false, error: null });
    }, [])
  };
}

// 专门用于API调用的Hook
export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
) {
  return useAsync(apiCall, dependencies, { immediate: true });
}

// 用于延迟加载的Hook
export function useLazyAsync<T>(asyncFunction: () => Promise<T>) {
  return useAsync(asyncFunction, [], { immediate: false });
} 