import api from './api';

export const userService = {
  // Get all users (Admin only)
  getAllUsers: async (params = {}) => {
    const response = await api.get('/admin/users', { params });
    return response.data;
  },

  // Update user role (Admin only)
  updateUserRole: async (userId, role) => {
    const response = await api.put(`/admin/users/${userId}/role`, null, {
      params: { role },
    });
    return response.data;
  },

  // Delete user (Admin only)
  deleteUser: async (userId) => {
    await api.delete(`/admin/users/${userId}`);
  },
};

export default userService;
