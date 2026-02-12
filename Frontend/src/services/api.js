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
    if (error.response) {
      const status = error.response.status;
      const requestUrl = error.config?.url || '';
      const isAuthEndpoint = requestUrl.includes('/auth/login') || requestUrl.includes('/auth') || requestUrl.includes('/users');
      const currentPath = window.location.pathname;
      console.error(`API Error: ${status} on ${requestUrl}`, error.response.data);
      // Handle 401 Unauthorized
      if (status === 401) {
        if (isAuthEndpoint || currentPath === '/login' || currentPath === '/register') {
          return Promise.reject(error);
        }
        const { store } = await import('../store');
        const { wsManager } = await import('./websocketManager');
        const { clearNotifications } = await import('../store/slices/notificationSlice');
        const { logout } = await import('../store/slices/authSlice');
        
        wsManager.disconnect();
        store.dispatch(clearNotifications());
        store.dispatch(logout());
        
        window.location.href = '/login';
      }
      
      if (status === 403) {
        console.log('Received 403 Forbidden response. Redirecting to /forbidden page.');
        if (currentPath === '/forbidden') {
          const { store } = await import('../store');
          store.dispatch(logout());
          return Promise.reject(error);
        }

        window.location.href = '/forbidden';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
