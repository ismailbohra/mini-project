import api from './api';
import { postService } from './postService';
import { commentService } from './commentService';

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

  // Get all posts (Moderator) - uses common endpoint
  getAllPosts: async (params = {}) => {
    return await postService.getPosts(params);
  },

  // Update any post (Moderator) - uses common endpoint with role-based permissions
  updateAnyPost: async (postId, postData) => {
    return await postService.updatePost(postId, postData);
  },

  // Delete any post (Moderator) - uses common endpoint with role-based permissions
  deleteAnyPost: async (postId, reportId = null) => {
    await postService.deletePost(postId);
    // If report_id is provided, mark it as deleted
    if (reportId) {
      try {
        await moderatorService.updatePostReportStatus(reportId, 'Deleted');
      } catch (error) {
        console.error('Failed to update report status after deletion:', error);
      }
    }
  },

  // Update any comment (Moderator) - uses common endpoint with role-based permissions
  updateAnyComment: async (commentId, commentData) => {
    return await commentService.updateComment(commentId, commentData);
  },

  // Delete any comment (Moderator) - uses common endpoint with role-based permissions
  deleteAnyComment: async (commentId, reportId = null) => {
    await commentService.deleteComment(commentId);
    // If report_id is provided, mark it as deleted
    if (reportId) {
      try {
        await moderatorService.updateCommentReportStatus(reportId, 'Deleted');
      } catch (error) {
        console.error('Failed to update report status after deletion:', error);
      }
    }
  },
};

export default moderatorService;
