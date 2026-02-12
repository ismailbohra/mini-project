import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/slices/authSlice';
import { setFilters, setPagination } from '../store/slices/postSlice';
import { markAsRead, markAllAsRead, clearNotifications } from '../store/slices/notificationSlice';
import postService from '../services/postService';
import notificationService from '../services/notificationService';
import debounce from '../utils/debounce';
import { toast } from 'react-toastify';
import { formatDistanceToNow } from 'date-fns';
import { wsManager } from '../services/websocketManager';

const Header = ({ toggleSidebar }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { notifications, unreadCount } = useSelector((state) => state.notifications);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchRef = useRef(null);

  const handleLogout = () => {
    // Disconnect WebSocket BEFORE dispatching actions to avoid Redux errors
    wsManager.disconnect();
    dispatch(clearNotifications());
    dispatch(logout());
    navigate('/login');
  };

  const fetchSuggestions = useRef(
    debounce(async (query) => {
      if (query.length >= 2) {
        try {
          const results = await postService.getSearchSuggestions(query);
          setSuggestions(results);
          setShowSuggestions(true);
        } catch (error) {
          console.error('Failed to fetch suggestions:', error);
          setSuggestions([]);
        }
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 300)
  ).current;

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    fetchSuggestions(value);
    if (value.trim() === '') {
      dispatch(setFilters({ search: '' }));
      dispatch(setPagination({ page: 1 }));
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      dispatch(setFilters({ search: searchQuery.trim() }));
      dispatch(setPagination({ page: 1 }));
      setShowSuggestions(false);
      
      if (location.pathname !== '/') {
        navigate('/');
      }
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion.value);
    dispatch(setFilters({ search: suggestion.value }));
    dispatch(setPagination({ page: 1 }));
    setShowSuggestions(false);
    
    if (location.pathname !== '/') {
      navigate('/');
    }
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

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
      default:
        return 'New notification';
    }
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow">
      <div className="container-fluid">
        <button 
          className="btn btn-outline-light me-2" 
          onClick={toggleSidebar}
          type="button"
        >
          <i className="bi bi-list"></i>
        </button>
        
        <Link className="navbar-brand fw-bold" to="/">
          Forum
        </Link>

        {user && (user.role === 'Admin' || user.role === 'Moderator') && (
          <span className="badge bg-warning text-dark ms-2">
            {user.role}
          </span>
        )}

        <form className="d-none d-md-flex mx-auto position-relative" style={{ width: '40%' }} onSubmit={handleSearch} ref={searchRef}>
          <div className="input-group">
            <input
              className="form-control"
              type="search"
              placeholder="Search posts..."
              value={searchQuery}
              onChange={handleSearchChange}
              onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            />
            <button className="btn btn-outline-light" type="submit">
              <i className="bi bi-search"></i>
            </button>
          </div>
          
          {showSuggestions && suggestions.length > 0 && (
            <div 
              className="position-absolute w-100 mt-1 bg-white border rounded shadow-lg" 
              style={{ top: '100%', zIndex: 1000, maxHeight: '300px', overflowY: 'auto' }}
            >
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="p-2 cursor-pointer border-bottom"
                  style={{ cursor: 'pointer' }}
                  onMouseDown={() => handleSuggestionClick(suggestion)}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f8f9fa'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                >
                  <div className="d-flex align-items-center">
                    <span className="badge bg-secondary me-2" style={{ fontSize: '0.7rem' }}>
                      {suggestion.type}
                    </span>
                    <span className="text-dark">{suggestion.value}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </form>

        <div className="d-flex align-items-center">
          <div className="dropdown me-3">
            <button
              className="btn btn-outline-light position-relative"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i className="bi bi-bell"></i>
              {unreadCount > 0 && (
                <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                  {unreadCount > 99 ? '99+' : unreadCount}
                </span>
              )}
            </button>
            <ul className="dropdown-menu dropdown-menu-end" style={{ minWidth: '350px', maxHeight: '400px', overflowY: 'auto' }}>
              <li className="d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
                <h6 className="mb-0">Notifications</h6>
                {unreadCount > 0 && (
                  <button 
                    className="btn btn-sm btn-link text-decoration-none p-0"
                    onClick={handleMarkAllAsRead}
                  >
                    Mark all read
                  </button>
                )}
              </li>
              {notifications.length > 0 ? (
                notifications.slice(0, 10).map((notif) => (
                  <li key={notif.id}>
                    <button
                      className={`dropdown-item ${!notif.is_read ? 'bg-light' : ''}`}
                      onClick={() => handleNotificationClick(notif)}
                      style={{ cursor: 'pointer', whiteSpace: 'normal' }}
                    >
                      <div className="d-flex align-items-start">
                        <i className={`bi ${notif.type && notif.type.includes('comment') ? 'bi-chat-dots' : 'bi-heart'} me-2 mt-1`}></i>
                        <div className="flex-grow-1">
                          <div className="fw-bold small">{getNotificationMessage(notif)}</div>
                          <small className="text-muted">
                            {formatDistanceToNow(new Date(notif.created_at), { addSuffix: true })}
                          </small>
                        </div>
                        {!notif.is_read && (
                          <span className="badge bg-primary rounded-pill ms-2">New</span>
                        )}
                      </div>
                    </button>
                  </li>
                ))
              ) : (
                <li>
                  <span className="dropdown-item text-muted text-center">No notifications</span>
                </li>
              )}
              {notifications.length > 0 && (
                <li className="border-top">
                  <button
                    className="dropdown-item text-center text-primary fw-bold"
                    onClick={() => navigate('/notifications')}
                  >
                    View All Notifications
                  </button>
                </li>
              )}
            </ul>
          </div>

          <div className="dropdown">
            <button
              className="btn btn-outline-light dropdown-toggle"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              {user?.profile_image ? (
                <img
                  src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${user.profile_image}`}
                  alt={user.username}
                  className="rounded-circle me-1"
                  style={{ width: '24px', height: '24px', objectFit: 'cover' }}
                />
              ) : (
                <i className="bi bi-person-circle me-1"></i>
              )}
              {user?.username || 'User'}
            </button>
            <ul className="dropdown-menu dropdown-menu-end">
              <li>
                <Link className="dropdown-item" to="/profile">
                  <i className="bi bi-person me-2"></i>
                  View Profile
                </Link>
              </li>
              <li><hr className="dropdown-divider" /></li>
              <li>
                <button className="dropdown-item text-danger" onClick={handleLogout}>
                  <i className="bi bi-box-arrow-right me-2"></i>
                  Logout
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Header;
