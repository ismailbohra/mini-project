import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: {
    indexes: null, // Use repeat style for arrays: tags[]=1&tags[]=2
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

      // Handle 401 Unauthorized
      if (status === 401) {


        if (isAuthEndpoint || currentPath === '/login' || currentPath === '/register') {

          return Promise.reject(error);
        }

        // Check if this is a role change error
        const responseData = error.response?.data || {};
        const errorMessage = responseData.detail || responseData.error?.message || responseData.message || '';


        const isRoleChanged = errorMessage.toLowerCase().includes('role has been modified') ||
          errorMessage.toLowerCase().includes('role has changed');


        // Determine redirect path
        const redirectPath = (isRoleChanged && currentPath !== '/role-changed')
          ? '/role-changed'
          : (currentPath !== '/login' ? '/login' : null);

        if (!redirectPath) {

          return Promise.reject(error);
        }



        const { store } = await import('../store');
        const { wsManager } = await import('./websocketManager');
        const { clearNotifications } = await import('../store/slices/notificationSlice');
        const { logout } = await import('../store/slices/authSlice');


        wsManager.disconnect();

        localStorage.clear();
        sessionStorage.clear();
        store.dispatch(clearNotifications());
        store.dispatch(logout());


        window.location.href = redirectPath;

        return Promise.reject(error);
      }

      if (status === 403) {

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
