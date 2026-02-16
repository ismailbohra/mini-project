import { use } from 'react';
import api from './api';

export const userService = {
  // Get all users (Admin only)
  getAllUsers: async (params = {}) => {
    const response = await api.get('/admin/users', { params });
    return response.data;
  },

  // Update user role (Admin only)
  updateUserRole: async (userId, role) => {
    const response = await api.post(`/admin/assign-role`, {
      user_id: userId,
      role: role,
    });
    return response.data;
  },

  // Toggle user active status (Admin only)
  toggleUser: async (userId) => {
    const response = await api.patch(`/admin/users/${userId}/toggle`);
    return response.data;
  },

  dasboardAnalytics: async () => {
    const response = await api.get('/admin/dashboard/analytics');
    return response.data;
  },
};

export default userService;
