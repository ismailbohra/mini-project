import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { formatDistanceToNow } from 'date-fns';
import notificationService from '../services/notificationService';
import { setNotifications, markAsRead, markAllAsRead } from '../store/slices/notificationSlice';

const Notifications = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { notifications, unreadCount } = useSelector((state) => state.notifications);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all', 'unread', 'read'

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const data = await notificationService.getNotifications(0, 100);
      dispatch(setNotifications(data));
    } catch (error) {
      console.error('Failed to load notifications:', error);
      toast.error('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationClick = async (notification) => {
    try {
      if (!notification.is_read) {
        await notificationService.markAsRead(notification.id);
        dispatch(markAsRead(notification.id));
      }

      if (notification.post_id) {
        navigate(`/post/${notification.post_id}`);
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      toast.error('Failed to mark notification as read');
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationService.markAsRead(notificationId);
      dispatch(markAsRead(notificationId));
      toast.success('Notification marked as read');
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      toast.error('Failed to mark notification as read');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      dispatch(markAllAsRead());
      toast.success('All notifications marked as read');
    } catch (error) {
      console.error('Failed to mark all as read:', error);
      toast.error('Failed to mark all as read');
    }
  };

  const getNotificationMessage = (notification) => {
    const actorName = notification.actor_username || 'Someone';
    switch (notification.type) {
      case 'comment_created':
        return `${actorName} commented on your post`;
      case 'comment_replied':
        return `${actorName} replied to your comment`;
      case 'post_liked':
        return `${actorName} liked your post`;
      case 'comment_liked':
        return `${actorName} liked your comment`;
      case 'post_user_mentioned':
        return `@${actorName} mentioned you in a post`;
      case 'comment_user_mentioned':
        return `@${actorName} mentioned you in a comment`;
      default:
        return 'New notification';
    }
  };

  const getNotificationIcon = (type) => {
    if (type && type.includes('mentioned')) {
      return 'bi-at text-warning';
    } else if (type && type.includes('comment')) {
      return 'bi-chat-dots text-info';
    } else if (type && type.includes('liked')) {
      return 'bi-heart-fill text-danger';
    }
    return 'bi-bell text-primary';
  };

  const filteredNotifications = notifications.filter((notif) => {
    if (filter === 'unread') return !notif.is_read;
    if (filter === 'read') return notif.is_read;
    return true;
  });

  if (loading) {
    return (
      <div className="container">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid">
      <div className="row mb-4">
        <div className="col">
          <div className="d-flex justify-content-between align-items-center">
            <h2>
              <i className="bi bi-bell me-2"></i>
              Notifications
              {unreadCount > 0 && (
                <span className="badge bg-danger ms-2">
                  {unreadCount > 99 ? '99+' : unreadCount}
                </span>
              )}
            </h2>
            {unreadCount > 0 && (
              <button
                className="btn btn-primary"
                onClick={handleMarkAllAsRead}
              >
                <i className="bi bi-check-all me-2"></i>
                Mark All as Read
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="row mb-3">
        <div className="col">
          <div className="btn-group" role="group">
            <button
              type="button"
              className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setFilter('all')}
            >
              All ({notifications.length})
            </button>
            <button
              type="button"
              className={`btn ${filter === 'unread' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setFilter('unread')}
            >
              Unread ({unreadCount})
            </button>
            <button
              type="button"
              className={`btn ${filter === 'read' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setFilter('read')}
            >
              Read ({notifications.length - unreadCount})
            </button>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-lg-8 col-md-10 mx-auto">
          {filteredNotifications.length > 0 ? (
            <div className="list-group">
              {filteredNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`list-group-item list-group-item-action ${
                    !notification.is_read ? 'bg-light border-primary' : ''
                  }`}
                >
                  <div className="d-flex w-100 justify-content-between align-items-start">
                    <div className="d-flex flex-grow-1" style={{ cursor: 'pointer' }} onClick={() => handleNotificationClick(notification)}>
                      <div className="me-3 mt-1">
                        <i className={`bi ${getNotificationIcon(notification.type)} fs-4`}></i>
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">
                          {getNotificationMessage(notification)}
                          {!notification.is_read && (
                            <span className="badge bg-primary ms-2">New</span>
                          )}
                        </h6>
                        <small className="text-muted">
                          <i className="bi bi-clock me-1"></i>
                          {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                        </small>
                        {notification.post_id && (
                          <div className="mt-2">
                            <small className="text-primary">
                              <i className="bi bi-arrow-right-circle me-1"></i>
                              Click to view post
                            </small>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="ms-2">
                      {!notification.is_read && (
                        <button
                          className="btn btn-sm btn-outline-primary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMarkAsRead(notification.id);
                          }}
                          title="Mark as read"
                        >
                          <i className="bi bi-check"></i>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card text-center py-5">
              <div className="card-body">
                <i className="bi bi-bell-slash display-1 text-muted mb-3"></i>
                <h5 className="text-muted">
                  {filter === 'unread' ? 'No unread notifications' : 
                   filter === 'read' ? 'No read notifications' : 
                   'No notifications yet'}
                </h5>
                <p className="text-muted">
                  {filter === 'all' && "You'll receive notifications when others interact with your posts and comments."}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Notifications;
