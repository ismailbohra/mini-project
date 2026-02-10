import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  postReports: [],
  commentReports: [],
  loading: false,
  error: null,
};

const reportSlice = createSlice({
  name: 'reports',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setPostReports: (state, action) => {
      state.postReports = action.payload;
      state.loading = false;
      state.error = null;
    },
    setCommentReports: (state, action) => {
      state.commentReports = action.payload;
      state.loading = false;
      state.error = null;
    },
    updatePostReport: (state, action) => {
      const index = state.postReports.findIndex(report => report.id === action.payload.id);
      if (index !== -1) {
        state.postReports[index] = action.payload;
      }
    },
    updateCommentReport: (state, action) => {
      const index = state.commentReports.findIndex(report => report.id === action.payload.id);
      if (index !== -1) {
        state.commentReports[index] = action.payload;
      }
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.loading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setLoading,
  setPostReports,
  setCommentReports,
  updatePostReport,
  updateCommentReport,
  setError,
  clearError,
} = reportSlice.actions;

export default reportSlice.reducer;
