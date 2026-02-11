import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/slices/authSlice';
import { setFilters, setPagination } from '../store/slices/postSlice';
import postService from '../services/postService';
import debounce from '../utils/debounce';

const Header = ({ toggleSidebar }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchRef = useRef(null);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  // Debounced function to fetch suggestions
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

  // Handle search input change
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    fetchSuggestions(value);
    // If search bar is cleared, reset search filter and pagination
    if (value.trim() === '') {
      dispatch(setFilters({ search: '' }));
      dispatch(setPagination({ page: 1 }));
    }
  };

  // Handle search submission
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Update Redux store with search query
      dispatch(setFilters({ search: searchQuery.trim() }));
      dispatch(setPagination({ page: 1 }));
      setShowSuggestions(false);
      
      // Navigate to home if not already there
      if (location.pathname !== '/') {
        navigate('/');
      }
    }
  };

  // Handle suggestion selection
  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion.value);
    // Update Redux store with search query
    dispatch(setFilters({ search: suggestion.value }));
    dispatch(setPagination({ page: 1 }));
    setShowSuggestions(false);
    
    // Navigate to home if not already there
    if (location.pathname !== '/') {
      navigate('/');
    }
  };

  // Close suggestions when clicking outside
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

  const notifications = [
    { id: 1, message: 'New comment on your post' },
    { id: 2, message: 'Someone liked your post' },
    { id: 3, message: 'New reply to your comment' },
  ];

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
          
          {/* Search Suggestions Dropdown */}
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
          {/* Notifications */}
          <div className="dropdown me-3">
            <button
              className="btn btn-outline-light position-relative"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i className="bi bi-bell"></i>
              <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                {notifications.length}
              </span>
            </button>
            <ul className="dropdown-menu dropdown-menu-end" style={{ minWidth: '300px' }}>
              <li>
                <h6 className="dropdown-header">Notifications</h6>
              </li>
              {notifications.map((notif) => (
                <li key={notif.id}>
                  <Link className="dropdown-item" to="#">
                    <small>{notif.message}</small>
                  </Link>
                </li>
              ))}
              {notifications.length === 0 && (
                <li>
                  <span className="dropdown-item text-muted">No notifications</span>
                </li>
              )}
            </ul>
          </div>

          {/* Profile Dropdown */}
          <div className="dropdown">
            <button
              className="btn btn-outline-light dropdown-toggle"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i className="bi bi-person-circle me-1"></i>
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
