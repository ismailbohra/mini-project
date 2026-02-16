import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import postReducer from './slices/postSlice';
import commentReducer from './slices/commentSlice';
import userReducer from './slices/adminSlice';
import reportReducer from './slices/reportSlice';
import notificationReducer from './slices/notificationSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    posts: postReducer,
    comments: commentReducer,
    users: userReducer,
    reports: reportReducer,
    notifications: notificationReducer,
  },
});
