import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/slices/authSlice';

const Header = ({ toggleSidebar }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const [searchQuery, setSearchQuery] = useState('');

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    // TODO: Implement search functionality
    console.log('Search:', searchQuery);
  };

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

        <form className="d-none d-md-flex mx-auto" style={{ width: '40%' }} onSubmit={handleSearch}>
          <div className="input-group">
            <input
              className="form-control"
              type="search"
              placeholder="Search posts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button className="btn btn-outline-light" type="submit">
              <i className="bi bi-search"></i>
            </button>
          </div>
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
