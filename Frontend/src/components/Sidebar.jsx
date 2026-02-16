import React from 'react';
import { NavLink } from 'react-router-dom';
import { useSelector } from 'react-redux';

const Sidebar = ({ isOpen }) => {
  const { user } = useSelector((state) => state.auth);
  const { unreadCount } = useSelector((state) => state.notifications);

  const menuItems = [
    { path: '/home', label: 'Home', icon: 'bi-house', roles: ['User', 'Moderator', 'Admin'] },
    { path: '/my-posts', label: 'My Posts', icon: 'bi-file-text', roles: ['User', 'Moderator', 'Admin'] },
    { path: '/create-post', label: 'Create Post', icon: 'bi-plus-circle', roles: ['User', 'Moderator', 'Admin'] },
    { path: '/notifications', label: 'Notifications', icon: 'bi-bell', roles: ['User', 'Moderator', 'Admin'] },
    { path: '/dashboard', label: 'Dashboard', icon: 'bi-speedometer2', roles: ['Admin'] },
    { path: '/review', label: 'Review', icon: 'bi-flag', roles: ['Moderator', 'Admin'] },
    { path: '/users', label: 'Users', icon: 'bi-people', roles: ['Admin'] },
  ];

  const filteredMenuItems = menuItems.filter((item) => {
    if (!user) return false;
    return item.roles.includes(user.role);
  });

  return (
    <div
      className={`bg-light border-end vh-100 position-fixed ${isOpen ? '' : 'd-none'}`}
      style={{ width: '250px', top: '56px', left: 0, overflowY: 'auto', zIndex: 1000 }}
    >
      <div className="list-group list-group-flush">
        {filteredMenuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `list-group-item list-group-item-action ${isActive ? 'active' : ''} ${
                item.disabled ? 'disabled' : ''
              }`
            }
            style={{ pointerEvents: item.disabled ? 'none' : 'auto' }}
          >
            <i className={`bi ${item.icon} me-2`}></i>
            {item.label}
            {item.path === '/notifications' && unreadCount > 0 && (
              <span className="badge bg-danger rounded-pill ms-2">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
            {/* {item.disabled && <small className="text-muted ms-2">(Coming Soon)</small>} */}
          </NavLink>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
