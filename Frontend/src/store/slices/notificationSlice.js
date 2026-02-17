import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  notifications: [],
  unreadCount: 0,
  isConnected: false,
  loading: false,
  error: null,
  initialLoadComplete: false,
};

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    setNotifications: (state, action) => {
      // Deduplicate notifications based on unique constraint criteria
      const uniqueNotifications = [];
      const seen = new Set();
      
      for (const notification of action.payload) {
        const key = `${notification.receiver_id}-${notification.actor_id}-${notification.type}-${notification.post_id || 'null'}-${notification.comment_id || 'null'}`;
        if (!seen.has(key)) {
          seen.add(key);
          uniqueNotifications.push(notification);
        }
      }
      
      state.notifications = uniqueNotifications;
      state.unreadCount = uniqueNotifications.filter(n => !n.is_read).length;
      state.initialLoadComplete = true;
    },
    addNotification: (state, action) => {
      const newNotification = action.payload;
      // Check both by ID and by unique constraint criteria
      const existsById = state.notifications.some(n => n.id === newNotification.id);
      const existsByContent = state.notifications.some(n => 
        n.receiver_id === newNotification.receiver_id &&
        n.actor_id === newNotification.actor_id &&
        n.type === newNotification.type &&
        (n.post_id || null) === (newNotification.post_id || null) &&
        (n.comment_id || null) === (newNotification.comment_id || null)
      );
      
      if (!existsById && !existsByContent) {
        state.notifications = [newNotification, ...state.notifications];
        if (!newNotification.is_read) {
          state.unreadCount += 1;
        }
      } else {
        console.log('[NotificationSlice] Duplicate notification blocked:', newNotification);
      }
    },
    markAsRead: (state, action) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification && !notification.is_read) {
        notification.is_read = true;
        state.unreadCount = Math.max(0, state.unreadCount - 1);
      }
    },
    markAllAsRead: (state) => {
      state.notifications.forEach(n => {
        n.is_read = true;
      });
      state.unreadCount = 0;
    },
    setUnreadCount: (state, action) => {
      state.unreadCount = action.payload;
    },
    incrementUnread: (state) => {
      state.unreadCount += 1;
    },
    decrementUnread: (state) => {
      state.unreadCount = Math.max(0, state.unreadCount - 1);
    },
    setConnected: (state, action) => {
      state.isConnected = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearNotifications: (state) => {
      state.notifications = [];
      state.unreadCount = 0;
      state.isConnected = false;
      state.initialLoadComplete = false;
    },
  },
});

export const {
  setNotifications,
  addNotification,
  markAsRead,
  markAllAsRead,
  setUnreadCount,
  incrementUnread,
  decrementUnread,
  setConnected,
  setLoading,
  setError,
  clearNotifications,
} = notificationSlice.actions;

export default notificationSlice.reducer;
