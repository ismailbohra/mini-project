import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { toast, ToastContainer } from 'react-toastify';
import { setUser } from '../store/slices/authSlice';
import authService from '../services/authService';

const Profile = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const [loadingPassword, setLoadingPassword] = useState(false);
  const [loadingUsername, setLoadingUsername] = useState(false);
  
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmNewPassword: '',
  });

  const [username, setUsername] = useState(user?.username || '');

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (passwordData.newPassword !== passwordData.confirmNewPassword) {
      toast.error('New passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoadingPassword(true);
    try {
      await authService.updatePassword(passwordData.currentPassword, passwordData.newPassword);
      toast.success('Password updated successfully');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmNewPassword: '',
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update password');
    } finally {
      setLoadingPassword(false);
    }
  };

  const handleUsernameSubmit = async (e) => {
    e.preventDefault();
    
    if (!username.trim()) {
      toast.error('Username cannot be empty');
      return;
    }

    setLoadingUsername(true);
    try {
      const updatedUser = await authService.updateUsername(username);
      dispatch(setUser(updatedUser));
      toast.success('Username updated successfully');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update username');
    } finally {
      setLoadingUsername(false);
    }
  };

  return (
    <div className="container">
      <ToastContainer position="top-right" autoClose={3000} />
      
      <h2 className="mb-4">
        <i className="bi bi-person-circle me-2"></i>
        Profile Settings
      </h2>

      {/* User Info Card */}
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-primary text-white">
          <h5 className="mb-0">Account Information</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-6 mb-3">
              <label className="fw-bold">Username:</label>
              <p className="mb-0">{user?.username}</p>
            </div>
            <div className="col-md-6 mb-3">
              <label className="fw-bold">Email:</label>
              <p className="mb-0">{user?.email}</p>
            </div>
            <div className="col-md-6 mb-3">
              <label className="fw-bold">Role:</label>
              <p className="mb-0">
                <span className={`badge ${
                  user?.role === 'Admin' ? 'bg-danger' : 
                  user?.role === 'Moderator' ? 'bg-warning' : 
                  'bg-info'
                }`}>
                  {user?.role}
                </span>
              </p>
            </div>
            <div className="col-md-6 mb-3">
              <label className="fw-bold">Member Since:</label>
              <p className="mb-0">{user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Update Username Card */}
      <div className="card shadow-sm mb-4">
        <div className="card-header">
          <h5 className="mb-0">Update Username</h5>
        </div>
        <div className="card-body">
          <form onSubmit={handleUsernameSubmit}>
            <div className="mb-3">
              <label htmlFor="username" className="form-label">
                New Username
              </label>
              <input
                type="text"
                className="form-control"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
              <small className="text-muted">Current: {user?.username}</small>
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loadingUsername || username === user?.username}
            >
              {loadingUsername ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2"></span>
                  Updating...
                </>
              ) : (
                <>
                  <i className="bi bi-check-circle me-2"></i>
                  Update Username
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Change Password Card */}
      <div className="card shadow-sm mb-4">
        <div className="card-header">
          <h5 className="mb-0">Change Password</h5>
        </div>
        <div className="card-body">
          <form onSubmit={handlePasswordSubmit}>
            <div className="mb-3">
              <label htmlFor="currentPassword" className="form-label">
                Current Password
              </label>
              <input
                type="password"
                className="form-control"
                id="currentPassword"
                name="currentPassword"
                value={passwordData.currentPassword}
                onChange={handlePasswordChange}
                required
              />
            </div>
            <div className="mb-3">
              <label htmlFor="newPassword" className="form-label">
                New Password
              </label>
              <input
                type="password"
                className="form-control"
                id="newPassword"
                name="newPassword"
                value={passwordData.newPassword}
                onChange={handlePasswordChange}
                required
                minLength={6}
              />
              <small className="text-muted">Minimum 6 characters</small>
            </div>
            <div className="mb-3">
              <label htmlFor="confirmNewPassword" className="form-label">
                Confirm New Password
              </label>
              <input
                type="password"
                className="form-control"
                id="confirmNewPassword"
                name="confirmNewPassword"
                value={passwordData.confirmNewPassword}
                onChange={handlePasswordChange}
                required
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loadingPassword}
            >
              {loadingPassword ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2"></span>
                  Updating...
                </>
              ) : (
                <>
                  <i className="bi bi-shield-check me-2"></i>
                  Change Password
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;
