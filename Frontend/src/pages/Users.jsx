import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import userService from '../services/userService';
import Pagination from '../components/Pagination';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [limit, setLimit] = useState(10);

  useEffect(() => {
    loadUsers();
  }, [currentPage, limit]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const params = {
        skip: (currentPage - 1) * limit,
        limit: limit,
      };
      const data = await userService.getAllUsers(params);
      setUsers(data);
      const total = Math.ceil((data.length || 0) / limit);
      setTotalPages(total);
    } catch (error) {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    if (!window.confirm(`Are you sure you want to change this user's role to ${newRole}?`)) {
      return;
    }

    try {
      await userService.updateUserRole(userId, newRole);
      toast.success('User role updated successfully');
      loadUsers();
    } catch (error) {
      toast.error(error.response?.data?.error?.message || 'Failed to update user role');
    }
  };

  const handleToggleUser = async (userId, isActive) => {
    const action = isActive ? 'deactivate' : 'activate';
    if (!window.confirm(`Are you sure you want to ${action} this user?`)) {
      return;
    }

    try {
      const updated = await userService.toggleUser(userId);
      toast.success(`User ${updated.is_active ? 'activated' : 'deactivated'} successfully`);
      loadUsers();
    } catch (error) {
      toast.error(error.response?.data?.error?.message || `Failed to ${action} user`);
    }
  };

  const handleLimitChange = (newLimit) => {
    setLimit(newLimit);
    setCurrentPage(1);
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'N/A';
    }
  };

  return (
    <div className="container-fluid">
      <div className="row mb-3">
        <div className="col">
          <h2>
            <i className="bi bi-people me-2"></i>
            User Management
          </h2>
          <p className="text-muted">Manage user roles and accounts</p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <>
          <div className="card shadow-sm">
            <div className="card-body">
              {/* 🔧 overflow fix */}
              <div
                className="table-responsive"
                style={{ overflow: 'visible' }}
              >
                <table className="table table-hover">
                  <thead className="table-light">
                    <tr>
                      <th>ID</th>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Registration Date</th>
                      <th>Change Role</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="text-center text-muted">
                          No users found
                        </td>
                      </tr>
                    ) : (
                      users.map((user) => (
                        <tr
                          key={user.id}
                          style={{ position: 'relative' }} // 🔧 row stacking fix
                        >
                          <td>{user.id}</td>
                          <td>
                            <i className="bi bi-person-circle me-2"></i>
                            {user.username}
                          </td>
                          <td>{user.email}</td>
                          <td>
                            <span
                              className={`badge ${
                                user.role === 'Admin'
                                  ? 'bg-danger'
                                  : user.role === 'Moderator'
                                  ? 'bg-warning'
                                  : 'bg-info'
                              }`}
                            >
                              {user.role}
                            </span>
                          </td>
                          <td>{formatDate(user.created_at)}</td>

                          {/* ✅ FIXED DROPDOWN */}
                          <td>
                            <div
                              className="dropdown d-inline-block"
                              style={{
                                position: 'static', // 🔧 critical fix
                              }}
                            >
                              <button
                                type="button"
                                className="btn btn-sm btn-primary dropdown-toggle"
                                data-bs-toggle="dropdown"
                                data-bs-display="static"
                                aria-expanded="false"
                              >
                                Change Role
                              </button>

                              <ul
                                className="dropdown-menu"
                                style={{
                                  zIndex: 1055, // 🔧 force top layer
                                }}
                              >
                                {user.role !== 'User' && (
                                  <li>
                                    <button
                                      className="dropdown-item"
                                      onClick={() =>
                                        handleRoleChange(user.id, 'User')
                                      }
                                    >
                                      User
                                    </button>
                                  </li>
                                )}
                                {user.role !== 'Moderator' && (
                                  <li>
                                    <button
                                      className="dropdown-item"
                                      onClick={() =>
                                        handleRoleChange(user.id, 'Moderator')
                                      }
                                    >
                                      Moderator
                                    </button>
                                  </li>
                                )}
                                {user.role !== 'Admin' && (
                                  <li>
                                    <button
                                      className="dropdown-item"
                                      onClick={() =>
                                        handleRoleChange(user.id, 'Admin')
                                      }
                                    >
                                      Admin
                                    </button>
                                  </li>
                                )}
                              </ul>
                            </div>
                          </td>

                          <td>
                            <div
                              className="form-check form-switch"
                              style={{ position: 'relative', zIndex: 1 }}
                            >
                              <input
                                className="form-check-input"
                                type="checkbox"
                                role="switch"
                                id={`statusToggle${user.id}`}
                                checked={user.is_active}
                                onChange={() =>
                                  handleToggleUser(user.id, user.is_active)
                                }
                                style={{ cursor: 'pointer' }}
                              />
                              <label
                                className="form-check-label"
                                htmlFor={`statusToggle${user.id}`}
                                style={{ cursor: 'pointer', userSelect: 'none' }}
                              >
                                {user.is_active ? 'Active' : 'Inactive'}
                              </label>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div className="mt-3">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              limit={limit}
              onLimitChange={handleLimitChange}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default Users;
