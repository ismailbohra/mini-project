import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Header from './Header';
import Sidebar from './Sidebar';
import { wsManager } from '../services/websocketManager';
import notificationService from '../services/notificationService';
import { setNotifications, setUnreadCount, clearNotifications } from '../store/slices/notificationSlice';
import { useNotificationToast } from '../hooks/useNotificationToast';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const dispatch = useDispatch();
  const { user, token, isAuthenticated } = useSelector((state) => state.auth);
  
  useNotificationToast();

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  useEffect(() => {
    if (isAuthenticated && user && token) {
      const initializeNotifications = async () => {
        try {
          const notifications = await notificationService.getNotifications();
          dispatch(setNotifications(notifications));
          
          const unreadCount = await notificationService.getUnreadCount();
          dispatch(setUnreadCount(unreadCount));
        } catch (error) {
          console.error('Failed to fetch notifications:', error);
        }
      };

      initializeNotifications();
      
      wsManager.connect(user.id, token);
    }

    return () => {
      if (!isAuthenticated) {
        dispatch(clearNotifications());
        wsManager.disconnect();
      }
    };
  }, [isAuthenticated, user, token, dispatch]);

  return (
    <div className="d-flex flex-column min-vh-100">
      <Header toggleSidebar={toggleSidebar} />
      <div className="d-flex flex-grow-1">
        <Sidebar isOpen={sidebarOpen} />
        <main className={`flex-grow-1 p-3 ${sidebarOpen ? '' : 'ms-0'}`} style={{ marginLeft: sidebarOpen ? '250px' : '0', transition: 'margin-left 0.3s' }}>
          <Outlet />
        </main>
      </div>
      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
};

export default Layout;
