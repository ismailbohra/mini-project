import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  posts: [],
  currentPost: null,
  loading: false,
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
} = postSlice.actions;

export default postSlice.reducer;
