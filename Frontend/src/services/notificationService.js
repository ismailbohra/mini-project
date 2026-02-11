import api from './api';

const notificationService = {
  getNotifications: async (skip = 0, limit = 50) => {
    const response = await api.get(`/notifications/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getUnreadCount: async () => {
    const response = await api.get('/notifications/unread/count');
    return response.data;
  },

  markAsRead: async (notificationId) => {
    const response = await api.patch(`/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllAsRead: async () => {
    await api.patch('/notifications/read-all');
  },
};

export default notificationService;
