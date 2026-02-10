import api from './api';

export const commentService = {
  // Get comments for a post
  getCommentsByPostId: async (postId, params = {}) => {
    const response = await api.get(`/comments/post/${postId}`, { params });
    return response.data;
  },

  // Create comment
  createComment: async (commentData) => {
    const response = await api.post('/comments', commentData);
    return response.data;
  },

  // Update comment
  updateComment: async (commentId, commentData) => {
    const response = await api.put(`/comments/${commentId}`, commentData);
    return response.data;
  },

  // Delete comment
  deleteComment: async (commentId) => {
    await api.delete(`/comments/${commentId}`);
  },

  // Like/Unlike comment
  likeComment: async (commentId) => {
    const response = await api.post(`/comments/${commentId}/like`);
    return response.data;
  },

  unlikeComment: async (commentId) => {
    await api.delete(`/comments/${commentId}/like`);
  },

  // Get comment likes count
  getCommentLikesCount: async (commentId) => {
    const response = await api.get(`/comments/${commentId}/likes/count`);
    return response.data;
  },

  // Report comment
  reportComment: async (commentId, reason) => {
    const response = await api.post(`/comments/${commentId}/report`, null, {
      params: { reason },
    });
    return response.data;
  },
};

export default commentService;
