import api from './api';

export const authService = {
  // Login
  login: async (email, password) => {
    
    const response = await api.post('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  // Register
  register: async (username, email, password) => {
    const response = await api.post('/users', {
      username,
      email,
      password,
    });
    return response.data;
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  // Update password
  updatePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/auth/change-password', {
      old_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  // Update username
  updateUsername: async (username) => {
    const response = await api.put('/users', { username });
    return response.data;
  },
};

export default authService;
