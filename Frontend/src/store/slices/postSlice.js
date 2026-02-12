import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  posts: [],
  currentPost: null,
  loading: false,
  newPostAdded: false,
  error: null,
  pagination: {
    total: 0,
    page: 1,
    limit: 10,
  },
  filters: {
    search: '',
    tags: [],
    sortBy: 'created_at',
    sortOrder: 'desc',
  },
};

const postSlice = createSlice({
  name: 'posts',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setPosts: (state, action) => {
      state.posts = action.payload;
      state.loading = false;
      state.error = null;
    },
    setCurrentPost: (state, action) => {
      state.currentPost = action.payload;
      state.loading = false;
    },
    addPost: (state, action) => {
      state.posts.unshift(action.payload);
    },
    updatePost: (state, action) => {
      const index = state.posts.findIndex(post => post.id === action.payload.id);
      if (index !== -1) {
        state.posts[index] = action.payload;
      }
      if (state.currentPost && state.currentPost.id === action.payload.id) {
        state.currentPost = action.payload;
      }
    },
    deletePost: (state, action) => {
      state.posts = state.posts.filter(post => post.id !== action.payload);
      if (state.currentPost && state.currentPost.id === action.payload) {
        state.currentPost = null;
      }
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.loading = false;
    },
    setPagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearError: (state) => {
      state.error = null;
    },
    updatePostLikesCount: (state, action) => {
      const { postId, likesCount, userHasLiked } = action.payload;
      console.log('[PostSlice] Updating post likes:', { postId, likesCount, userHasLiked });
      const post = state.posts.find(p => p.id === postId);
      if (post) {
        post.likes_count = likesCount;
        post.user_has_liked = userHasLiked;
        console.log('[PostSlice] Post updated in list:', post);
      }
      if (state.currentPost && state.currentPost.id === postId) {
        state.currentPost.likes_count = likesCount;
        state.currentPost.user_has_liked = userHasLiked;
        console.log('[PostSlice] Current post updated:', state.currentPost);
      }
    },
    updatePostCommentsCount: (state, action) => {
      const { postId, commentsCount } = action.payload;
      console.log('[PostSlice] Updating post comments count:', { postId, commentsCount });
      const post = state.posts.find(p => p.id === postId);
      if (post) {
        post.comments_count = commentsCount;
        console.log('[PostSlice] Post comments updated:', post);
      }
      if (state.currentPost && state.currentPost.id === postId) {
        state.currentPost.comments_count = commentsCount;
        console.log('[PostSlice] Current post comments updated:', state.currentPost);
      }
    },
    updateFullPost: (state, action) => {
      const updatedPost = action.payload;
      console.log('[PostSlice] Full post update:', updatedPost);
      const index = state.posts.findIndex(p => p.id === updatedPost.id);
      if (index !== -1) {
        state.posts[index] = updatedPost;
      }
      if (state.currentPost && state.currentPost.id === updatedPost.id) {
        state.currentPost = updatedPost;
      }
    },
    newPostAdded: (state, action) => {
      state.newPostAdded = true;
    },
  },
});

export const {
  setLoading,
  setPosts,
  setCurrentPost,
  addPost,
  updatePost,
  deletePost,
  setError,
  setPagination,
  setFilters,
  clearError,
  updatePostLikesCount,
  updatePostCommentsCount,
  updateFullPost,
  newPostAdded,
} = postSlice.actions;

export default postSlice.reducer;
