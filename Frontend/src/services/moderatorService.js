import api from './api';

export const moderatorService = {
  // Get pending post reports
  getPendingPostReports: async (params = {}) => {
    const response = await api.get('/moderator/reports/posts', { params });
    return response.data;
  },

  // Update post report status
  updatePostReportStatus: async (reportId, status) => {
    const response = await api.put(`/moderator/reports/posts/${reportId}/status`, null, {
      params: { status_value: status },
    });
    return response.data;
  },

  // Get pending comment reports
  getPendingCommentReports: async (params = {}) => {
    const response = await api.get('/moderator/reports/comments', { params });
    return response.data;
  },

  // Update comment report status
  updateCommentReportStatus: async (reportId, status) => {
    const response = await api.put(`/moderator/reports/comments/${reportId}/status`, null, {
      params: { status_value: status },
    });
    return response.data;
  },

  // Get all posts (Moderator)
  getAllPosts: async (params = {}) => {
    const response = await api.get('/moderator/posts', { params });
    return response.data;
  },

  // Update any post (Moderator)
  updateAnyPost: async (postId, postData) => {
    const response = await api.put(`/moderator/posts/${postId}`, postData);
    return response.data;
  },

  // Delete any post (Moderator)
  deleteAnyPost: async (postId) => {
    await api.delete(`/moderator/posts/${postId}`);
  },

  // Update any comment (Moderator)
  updateAnyComment: async (commentId, content) => {
    const response = await api.put(`/moderator/comments/${commentId}`, { content });
    return response.data;
  },

  // Delete any comment (Moderator)
  deleteAnyComment: async (commentId) => {
    await api.delete(`/moderator/comments/${commentId}`);
  },
};

export default moderatorService;
