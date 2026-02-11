import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import userService from '../services/userService';
import Pagination from '../components/Pagination';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const limit = 10;

  useEffect(() => {
    loadUsers();
  }, [currentPage]);

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
      toast.error(error.response?.data?.detail || 'Failed to update user role');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      await userService.deleteUser(userId);
      toast.success('User deleted successfully');
      loadUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    }
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
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead className="table-light">
                    <tr>
                      <th>ID</th>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Registration Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="text-center text-muted">
                          No users found
                        </td>
                      </tr>
                    ) : (
                      users.map((user) => (
                        <tr key={user.id}>
                          <td>{user.id}</td>
                          <td>
                            <i className="bi bi-person-circle me-2"></i>
                            {user.username}
                          </td>
                          <td>{user.email}</td>
                          <td>
                            <span className={`badge ${
                              user.role === 'Admin' ? 'bg-danger' :
                              user.role === 'Moderator' ? 'bg-warning' :
                              'bg-info'
                            }`}>
                              {user.role}
                            </span>
                          </td>
                          <td>{formatDate(user.created_at)}</td>
                          <td>
                            <div className="btn-group" role="group">
                              <button
                                type="button"
                                className="btn btn-sm btn-outline-primary dropdown-toggle"
                                data-bs-toggle="dropdown"
                              >
                                Change Role
                              </button>
                              <ul className="dropdown-menu">
                                <li>
                                  <button
                                    className="dropdown-item"
                                    onClick={() => handleRoleChange(user.id, 'User')}
                                    disabled={user.role === 'User'}
                                  >
                                    User
                                  </button>
                                </li>
                                <li>
                                  <button
                                    className="dropdown-item"
                                    onClick={() => handleRoleChange(user.id, 'Moderator')}
                                    disabled={user.role === 'Moderator'}
                                  >
                                    Moderator
                                  </button>
                                </li>
                                <li>
                                  <button
                                    className="dropdown-item"
                                    onClick={() => handleRoleChange(user.id, 'Admin')}
                                    disabled={user.role === 'Admin'}
                                  >
                                    Admin
                                  </button>
                                </li>
                              </ul>
                              <button
                                className="btn btn-sm btn-outline-danger"
                                onClick={() => handleDeleteUser(user.id)}
                              >
                                <i className="bi bi-trash"></i>
                              </button>
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
            />
          </div>
        </>
      )}
    </div>
  );
};

export default Users;
