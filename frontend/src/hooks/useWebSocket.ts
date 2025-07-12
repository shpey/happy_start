/**
 * WebSocket Hook
 * 提供WebSocket连接管理、消息发送接收、重连机制
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export interface WebSocketOptions {
  onMessage?: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  pingInterval?: number;
}

export interface WebSocketHookReturn {
  socket: WebSocket | null;
  isConnected: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  sendMessage: (message: any) => void;
  connect: () => void;
  disconnect: () => void;
  lastMessage: any;
  error: Event | null;
}

export const useWebSocket = (
  url: string,
  options: WebSocketOptions = {}
): WebSocketHookReturn => {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    pingInterval = 30000
  } = options;

  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [error, setError] = useState<Event | null>(null);

  const reconnectAttempts = useRef(0);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const pingTimer = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnect = useRef(true);

  // 清理定时器
  const clearTimers = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }
    if (pingTimer.current) {
      clearInterval(pingTimer.current);
      pingTimer.current = null;
    }
  }, []);

  // 发送心跳包
  const startPing = useCallback(() => {
    if (pingInterval > 0 && socket?.readyState === WebSocket.OPEN) {
      pingTimer.current = setInterval(() => {
        if (socket?.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: 'ping' }));
        }
      }, pingInterval);
    }
  }, [socket, pingInterval]);

  // 连接WebSocket
  const connect = useCallback(() => {
    if (socket?.readyState === WebSocket.OPEN || socket?.readyState === WebSocket.CONNECTING) {
      return;
    }

    try {
      setConnectionState('connecting');
      setError(null);
      
      const ws = new WebSocket(url);

      ws.onopen = (event) => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionState('connected');
        reconnectAttempts.current = 0;
        onConnect?.();
        startPing();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // 处理心跳响应
          if (data.type === 'pong') {
            return;
          }
          
          setLastMessage(data);
          onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setConnectionState('disconnected');
        clearTimers();
        onDisconnect?.();
        
        // 自动重连
        if (shouldReconnect.current && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          console.log(`Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts})...`);
          
          reconnectTimer.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError(event);
        setConnectionState('error');
        onError?.(event);
      };

      setSocket(ws);
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionState('error');
    }
  }, [url, onConnect, onMessage, onDisconnect, onError, startPing, maxReconnectAttempts, reconnectInterval, clearTimers]);

  // 断开连接
  const disconnect = useCallback(() => {
    shouldReconnect.current = false;
    clearTimers();
    
    if (socket) {
      socket.close(1000, 'Manual disconnect');
      setSocket(null);
    }
    
    setIsConnected(false);
    setConnectionState('disconnected');
  }, [socket, clearTimers]);

  // 发送消息
  const sendMessage = useCallback((message: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      try {
        const messageString = typeof message === 'string' ? message : JSON.stringify(message);
        socket.send(messageString);
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
      }
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', message);
    }
  }, [socket]);

  // 初始化连接
  useEffect(() => {
    shouldReconnect.current = true;
    connect();

    return () => {
      shouldReconnect.current = false;
      clearTimers();
      if (socket) {
        socket.close(1000, 'Component unmounting');
      }
    };
  }, [url]); // 只依赖url，避免重复连接

  // 清理资源
  useEffect(() => {
    return () => {
      clearTimers();
      if (socket) {
        socket.close(1000, 'Component unmounting');
      }
    };
  }, [socket, clearTimers]);

  return {
    socket,
    isConnected,
    connectionState,
    sendMessage,
    connect,
    disconnect,
    lastMessage,
    error
  };
}; 