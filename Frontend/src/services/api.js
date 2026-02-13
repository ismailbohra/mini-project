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
      
      console.log('=== API Error Debug ===');
      console.log('Status:', status);
      console.log('Request URL:', requestUrl);
      console.log('Current Path:', currentPath);
      console.log('Response Data:', error.response.data);
      console.error(`API Error: ${status} on ${requestUrl}`, error.response.data);
      
      // Handle 401 Unauthorized
      if (status === 401) {
        console.log('🔒 401 Unauthorized detected');
        
        if (isAuthEndpoint || currentPath === '/login' || currentPath === '/register') {
          console.log('⏭️ Skipping - auth endpoint or already on login/register');
          return Promise.reject(error);
        }
        
        // Check if this is a role change error
        const responseData = error.response?.data || {};
        const errorMessage = responseData.detail || responseData.error?.message || responseData.message || '';
        console.log('📝 Error message:', errorMessage);
        
        const isRoleChanged = errorMessage.toLowerCase().includes('role has been modified') || 
                             errorMessage.toLowerCase().includes('role has changed');
        console.log('🔄 Is role changed?', isRoleChanged);
        
        // Determine redirect path
        const redirectPath = (isRoleChanged && currentPath !== '/role-changed') 
          ? '/role-changed' 
          : (currentPath !== '/login' ? '/login' : null);
        
        if (!redirectPath) {
          console.log('✓ Already on target page, no redirect needed');
          return Promise.reject(error);
        }
        
        console.log('🔀 Will redirect to:', redirectPath);
        
        const { store } = await import('../store');
        const { wsManager } = await import('./websocketManager');
        const { clearNotifications } = await import('../store/slices/notificationSlice');
        const { logout } = await import('../store/slices/authSlice');
        
        // Disconnect WebSocket
        console.log('🧹 Cleaning up user session...');
        wsManager.disconnect();
        
        // Clear storage
        localStorage.clear();
        sessionStorage.clear();
        
        // Dispatch logout AFTER determining redirect path but BEFORE redirect
        store.dispatch(clearNotifications());
        store.dispatch(logout());
        
        // Perform redirect - this will cause a full page reload
        console.log(`✅ Redirecting to ${redirectPath}`);
        window.location.href = redirectPath;
        
        // Return rejected promise to prevent any further processing
        return Promise.reject(error);
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
