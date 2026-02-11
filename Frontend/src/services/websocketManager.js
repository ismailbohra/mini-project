import { store } from '../store';
import { addNotification, setConnected } from '../store/slices/notificationSlice';

class WebSocketManager {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.userId = null;
    this.reconnectTimer = null;
    this.isIntentionallyClosed = false;
  }

  connect(userId, token) {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.userId = userId;
    this.isIntentionallyClosed = false;
    
    const wsUrl = `ws://localhost:8000/notifications/ws`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      store.dispatch(setConnected(true));
      
      this.ws.send(JSON.stringify({ user_id: userId }));
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'notification' && data.notification) {
          store.dispatch(addNotification(data.notification));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      store.dispatch(setConnected(false));
      this.ws = null;

      if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
        this.reconnectTimer = setTimeout(() => {
          this.connect(userId, token);
        }, this.reconnectDelay);
      }
    };
  }

  disconnect() {
    this.isIntentionallyClosed = true;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.reconnectAttempts = 0;
    store.dispatch(setConnected(false));
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

export const wsManager = new WebSocketManager();
