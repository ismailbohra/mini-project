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
  register: async (username, email, password, profileImage = null) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('email', email);
    formData.append('password', password);
    if (profileImage) {
      formData.append('profile_image', profileImage);
    }
    const response = await api.post('/users', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
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

  // Update username, profile image and bio
  updateUser: async (username = null, profileImage = null, bio = null) => {
    const formData = new FormData();
    if (username) {
      formData.append('username', username);
    }
    if (bio !== null) {
      formData.append('bio', bio);
    }
    if (profileImage) {
      formData.append('profile_image', profileImage);
    }
    const response = await api.put('/users', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Keep backwards compatibility
  updateUsername: async (username) => {
    const formData = new FormData();
    formData.append('username', username);
    const response = await api.put('/users', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default authService;
