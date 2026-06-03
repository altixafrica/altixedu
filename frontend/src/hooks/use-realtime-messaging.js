import { useEffect, useRef, useCallback, useState } from 'react';

/**
 * Hook for real-time WebSocket messaging
 * Handles connection, reconnection, and message events
 */
export const useRealtimeMessaging = (onMessage, onTyping, onReadReceipt, onUserStatus) => {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  const reconnectAttempts = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 5;

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/messages/`;
      
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        
        // Send keep-alive ping every 30 seconds
        const pingInterval = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
        
        return () => clearInterval(pingInterval);
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'new_message':
              onMessage?.(data);
              break;
            case 'typing_indicator':
              onTyping?.(data);
              break;
            case 'read_receipt':
              onReadReceipt?.(data);
              break;
            case 'user_status':
              onUserStatus?.(data);
              break;
            case 'pong':
              // Keep-alive response
              break;
            default:
              break;
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.current.onerror = (err) => {
        console.error('WebSocket error:', err);
        setError('Connection error');
        setConnected(false);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setConnected(false);
        
        // Attempt reconnection
        if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectTimeout.current = setTimeout(() => {
            reconnectAttempts.current += 1;
            connect();
          }, delay);
        }
      };
    } catch (err) {
      console.error('WebSocket error:', err);
      setError(err.message);
    }
  }, [onMessage, onTyping, onReadReceipt, onUserStatus]);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    if (ws.current) {
      ws.current.close();
    }
  }, []);

  const send = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  }, []);

  const sendMessage = useCallback((receiver_id, content) => {
    send({
      type: 'message',
      receiver_id,
      content,
    });
  }, [send]);

  const sendTypingIndicator = useCallback((recipient_id, is_typing) => {
    send({
      type: 'typing',
      recipient_id,
      is_typing,
    });
  }, [send]);

  const sendReadReceipt = useCallback((message_id) => {
    send({
      type: 'read_receipt',
      message_id,
    });
  }, [send]);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    connected,
    error,
    sendMessage,
    sendTypingIndicator,
    sendReadReceipt,
  };
};

/**
 * Hook for tracking online users
 */
export const useOnlineUsers = () => {
  const [onlineUsers, setOnlineUsers] = useState(new Set());

  const handleUserStatus = useCallback((data) => {
    setOnlineUsers((prev) => {
      const newSet = new Set(prev);
      if (data.status === 'online') {
        newSet.add(data.user_id);
      } else {
        newSet.delete(data.user_id);
      }
      return newSet;
    });
  }, []);

  return { onlineUsers, handleUserStatus };
};

/**
 * Hook for tracking typing indicators
 */
export const useTypingIndicators = () => {
  const [typingUsers, setTypingUsers] = useState(new Map());

  const handleTyping = useCallback((data) => {
    setTypingUsers((prev) => {
      const newMap = new Map(prev);
      if (data.is_typing) {
        newMap.set(data.user_id, true);
      } else {
        newMap.delete(data.user_id);
      }
      return newMap;
    });
  }, []);

  const isTyping = useCallback((userId) => {
    return typingUsers.has(userId);
  }, [typingUsers]);

  return { typingUsers, handleTyping, isTyping };
};
