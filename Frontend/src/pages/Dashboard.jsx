import React, { useState, useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  setAnalyticsLoading,
  setAnalytics,
  setAnalyticsError,
} from '../store/slices/adminSlice';
import api from '../services/api';
import { toast } from 'react-toastify';
import './Dashboard.css';


const Dashboard = () => {
  const dispatch = useDispatch();
  const { analytics, analyticsLoading, activeUsersRealtime } = useSelector((state) => state.users);
  const { user } = useSelector((state) => state.auth);

  // Fetch dashboard analytics
  const fetchAnalytics = useCallback(async () => {
    try {
      dispatch(setAnalyticsLoading(true));
      const response = await api.get('/admin/dashboard/analytics');
      dispatch(setAnalytics(response.data));
    } catch (error) {
      console.error('Error fetching analytics:', error);
      dispatch(setAnalyticsError('Failed to load dashboard analytics'));
      toast.error('Failed to load dashboard analytics');
    }
  }, [dispatch]);


  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (analyticsLoading || !analytics) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>
          <i className="bi bi-speedometer2 me-2"></i>
          Admin Dashboard
        </h1>
        <p className="text-muted">Real-time analytics and insights</p>
      </div>

      {/* Key Metrics Cards */}
      <div className="metrics-grid">

        <div className="metric-card success">
          <div className="metric-icon">
            <i className="bi bi-person-check-fill"></i>
          </div>
          <div className="metric-content">
            <h3 className="realtime-counter">{activeUsersRealtime}</h3>
            <p>Online Users <span className="live-badge">LIVE</span></p>
          </div>
        </div>

        <div className="metric-card info">
          <div className="metric-icon">
            <i className="bi bi-file-post-fill"></i>
          </div>
          <div className="metric-content">
            <h3>{analytics.total_posts}</h3>
            <p>Total Posts</p>
          </div>
        </div>

        <div className="metric-card warning">
          <div className="metric-icon">
            <i className="bi bi-shield-fill-exclamation"></i>
          </div>
          <div className="metric-content">
            <h3>{analytics.admin_count}</h3>
            <p>Admins</p>
          </div>
        </div>

        <div className="metric-card moderator">
          <div className="metric-icon">
            <i className="bi bi-shield-check"></i>
          </div>
          <div className="metric-content">
            <h3>{analytics.moderator_count}</h3>
            <p>Moderators</p>
          </div>
        </div>

        <div className="metric-card user">
          <div className="metric-icon">
            <i className="bi bi-person-fill"></i>
          </div>
          <div className="metric-content">
            <h3>{analytics.normal_user_count}</h3>
            <p>Regular Users</p>
          </div>
        </div>
      </div>


      {/* User with Most Posts */}
      {analytics.user_with_most_posts && (
        <div className="featured-user-card">
          <h3 className="section-title">
            <i className="bi bi-trophy-fill me-2"></i>
            Top Content Creator
          </h3>
          <div className="featured-user-content">
            {analytics.user_with_most_posts.profile_image ? (
              <img
                src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${analytics.user_with_most_posts.profile_image}`}
                alt={analytics.user_with_most_posts.username}
                className="featured-avatar"
              />
            ) : (
              <div className="featured-avatar-placeholder">
                <i className="bi bi-person-fill"></i>
              </div>
            )}
            <div className="featured-user-info">
              <h4>{analytics.user_with_most_posts.username}</h4>
              <p className="post-count">
                <i className="bi bi-file-post me-1"></i>
                {analytics.user_with_most_posts.post_count} Posts
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Lists Grid */}
      <div className="lists-grid">
        {/* Top Mentioned Users */}
        <div className="list-card">
          <h3 className="list-title">
            <i className="bi bi-at me-2"></i>
            Top 5 Mentioned Users
          </h3>
          <div className="user-list">
            {analytics.top_5_mentioned_users.length > 0 ? (
              analytics.top_5_mentioned_users.map((user, index) => (
                <div key={user.user_id} className="user-list-item">
                  <div className="user-rank">{index + 1}</div>
                  {user.profile_image ? (
                    <img
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${user.profile_image}`}
                      alt={user.username}
                      className="user-avatar-small"
                    />
                  ) : (
                    <div className="user-avatar-small placeholder">
                      <i className="bi bi-person-fill"></i>
                    </div>
                  )}
                  <div className="user-info">
                    <span className="username">{user.username}</span>
                    <span className="user-stat">
                      <i className="bi bi-at me-1"></i>
                      {user.mention_count} mentions
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">No mentions yet</p>
            )}
          </div>
        </div>

        {/* Top Reported Users */}
        <div className="list-card">
          <h3 className="list-title">
            <i className="bi bi-flag-fill me-2"></i>
            Top 5 Reported Users
          </h3>
          <div className="user-list">
            {analytics.top_5_reported_users.length > 0 ? (
              analytics.top_5_reported_users.map((user, index) => (
                <div key={user.user_id} className="user-list-item">
                  <div className="user-rank danger">{index + 1}</div>
                  {user.profile_image ? (
                    <img
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${user.profile_image}`}
                      alt={user.username}
                      className="user-avatar-small"
                    />
                  ) : (
                    <div className="user-avatar-small placeholder">
                      <i className="bi bi-person-fill"></i>
                    </div>
                  )}
                  <div className="user-info">
                    <span className="username">{user.username}</span>
                    <span className="user-stat danger">
                      <i className="bi bi-flag-fill me-1"></i>
                      {user.report_count} reports
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">No reports yet</p>
            )}
          </div>
        </div>

        {/* Top Tags List */}
        <div className="list-card">
          <h3 className="list-title">
            <i className="bi bi-tags-fill me-2"></i>
            Popular Tags
          </h3>
          <div className="tags-list">
            {analytics.top_5_tags.length > 0 ? (
              analytics.top_5_tags.map((tag, index) => (
                <div key={tag.tag_id} className="tag-item">
                  <span className="tag-badge">#{tag.tag_name}</span>
                  <span className="tag-count">{tag.usage_count} uses</span>
                </div>
              ))
            ) : (
              <p className="no-data">No tags yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
