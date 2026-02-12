import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  comments: [],
  loading: false,
  error: null,
};

const commentSlice = createSlice({
  name: 'comments',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setComments: (state, action) => {
      state.comments = action.payload;
      state.loading = false;
      state.error = null;
    },
    addComment: (state, action) => {
      state.comments.unshift(action.payload);
    },
    addReply: (state, action) => {
      const { parentCommentId, reply } = action.payload;
      const addReplyRecursive = (comments, parentId, newReply) => {
        return comments.map(comment => {
          if (comment.id === parentId) {
            return {
              ...comment,
              replies: [...(comment.replies || []), newReply],
            };
          }
          if (comment.replies && comment.replies.length > 0) {
            return {
              ...comment,
              replies: addReplyRecursive(comment.replies, parentId, newReply),
            };
          }
          return comment;
        });
      };
      state.comments = addReplyRecursive(state.comments, parentCommentId, reply);
    },
    updateComment: (state, action) => {
      const updateCommentRecursive = (comments, updatedComment) => {
        return comments.map(comment => {
          if (comment.id === updatedComment.id) {
            return { ...comment, ...updatedComment };
          }
          if (comment.replies && comment.replies.length > 0) {
            return {
              ...comment,
              replies: updateCommentRecursive(comment.replies, updatedComment),
            };
          }
          return comment;
        });
      };
      state.comments = updateCommentRecursive(state.comments, action.payload);
    },
    deleteComment: (state, action) => {
      const deleteCommentRecursive = (comments, commentId) => {
        return comments.filter(comment => {
          if (comment.id === commentId) {
            return false;
          }
          if (comment.replies && comment.replies.length > 0) {
            comment.replies = deleteCommentRecursive(comment.replies, commentId);
          }
          return true;
        });
      };
      state.comments = deleteCommentRecursive(state.comments, action.payload);
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.loading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateCommentLikesCount: (state, action) => {
      const { commentId, likesCount, userHasLiked } = action.payload;
      console.log('[CommentSlice] Updating comment likes:', { commentId, likesCount, userHasLiked });
      const updateLikesRecursive = (comments) => {
        return comments.map(comment => {
          if (comment.id === commentId) {
            console.log('[CommentSlice] Comment found and updated:', commentId);
            return { ...comment, likes_count: likesCount, user_has_liked: userHasLiked };
          }
          if (comment.replies && comment.replies.length > 0) {
            return {
              ...comment,
              replies: updateLikesRecursive(comment.replies),
            };
          }
          return comment;
        });
      };
      state.comments = updateLikesRecursive(state.comments);
    },
  },
});

export const {
  setLoading,
  setComments,
  addComment,
  addReply,
  updateComment,
  deleteComment,
  setError,
  clearError,
  updateCommentLikesCount,
} = commentSlice.actions;

export default commentSlice.reducer;
