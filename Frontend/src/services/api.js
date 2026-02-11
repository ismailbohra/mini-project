import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && error.response.status === 401) {
      // Token expired or invalid - clean up and redirect
      // Import store dynamically to avoid circular dependencies
      const { store } = await import('../store');
      const { wsManager } = await import('./websocketManager');
      const { clearNotifications } = await import('../store/slices/notificationSlice');
      const { logout } = await import('../store/slices/authSlice');
      
      // Disconnect WebSocket and clear state
      wsManager.disconnect();
      store.dispatch(clearNotifications());
      store.dispatch(logout());
      
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
