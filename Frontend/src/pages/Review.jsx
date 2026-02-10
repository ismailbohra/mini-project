import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import { formatDistanceToNow } from 'date-fns';
import moderatorService from '../services/moderatorService';

const Review = () => {
  const [activeTab, setActiveTab] = useState('posts');
  const [postReports, setPostReports] = useState([]);
  const [commentReports, setCommentReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReports();
  }, [activeTab]);

  const loadReports = async () => {
    setLoading(true);
    try {
      if (activeTab === 'posts') {
        const data = await moderatorService.getPendingPostReports();
        setPostReports(data);
      } else {
        const data = await moderatorService.getPendingCommentReports();
        setCommentReports(data);
      }
    } catch (error) {
      toast.error('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const handlePostReportStatus = async (reportId, status) => {
    try {
      await moderatorService.updatePostReportStatus(reportId, status);
      toast.success(`Report ${status.toLowerCase()}`);
      loadReports();
    } catch (error) {
      toast.error('Failed to update report status');
    }
  };

  const handleCommentReportStatus = async (reportId, status) => {
    try {
      await moderatorService.updateCommentReportStatus(reportId, status);
      toast.success(`Report ${status.toLowerCase()}`);
      loadReports();
    } catch (error) {
      toast.error('Failed to update report status');
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;

    try {
      await moderatorService.deleteAnyPost(postId);
      toast.success('Post deleted successfully');
      loadReports();
    } catch (error) {
      toast.error('Failed to delete post');
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) return;

    try {
      await moderatorService.deleteAnyComment(commentId);
      toast.success('Comment deleted successfully');
      loadReports();
    } catch (error) {
      toast.error('Failed to delete comment');
    }
  };

  const formatDate = (dateString) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="container-fluid">
      <ToastContainer position="top-right" autoClose={3000} />
      
      <div className="row mb-4">
        <div className="col">
          <h2>
            <i className="bi bi-flag me-2"></i>
            Content Review
          </h2>
          <p className="text-muted">Review and manage reported content</p>
        </div>
      </div>

      {/* Tabs */}
      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'posts' ? 'active' : ''}`}
            onClick={() => setActiveTab('posts')}
          >
            <i className="bi bi-file-text me-2"></i>
            Post Reports
            {postReports.length > 0 && (
              <span className="badge bg-danger ms-2">{postReports.length}</span>
            )}
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'comments' ? 'active' : ''}`}
            onClick={() => setActiveTab('comments')}
          >
            <i className="bi bi-chat me-2"></i>
            Comment Reports
            {commentReports.length > 0 && (
              <span className="badge bg-danger ms-2">{commentReports.length}</span>
            )}
          </button>
        </li>
      </ul>

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <>
          {/* Post Reports */}
          {activeTab === 'posts' && (
            <div>
              {postReports.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-check-circle display-1 text-success"></i>
                  <p className="text-muted mt-3">No pending post reports</p>
                </div>
              ) : (
                postReports.map((report) => (
                  <div key={report.id} className="card shadow-sm mb-3">
                    <div className="card-body">
                      <div className="d-flex justify-content-between align-items-start mb-3">
                        <div>
                          <h5 className="card-title mb-1">
                            <Link to={`/post/${report.post_id}`} className="text-decoration-none">
                              Post #{report.post_id}
                            </Link>
                          </h5>
                          <p className="text-muted small mb-0">
                            Reported {formatDate(report.created_at)} by User #{report.user_id}
                          </p>
                        </div>
                        <span className={`badge ${
                          report.status === 'Pending' ? 'bg-warning' :
                          report.status === 'Reviewed' ? 'bg-success' :
                          'bg-secondary'
                        }`}>
                          {report.status}
                        </span>
                      </div>

                      <div className="mb-3">
                        <strong>Reason:</strong>
                        <p className="mb-0">{report.reason}</p>
                      </div>

                      <div className="btn-group" role="group">
                        <Link
                          to={`/post/${report.post_id}`}
                          className="btn btn-sm btn-outline-primary"
                        >
                          <i className="bi bi-eye me-1"></i>
                          View Post
                        </Link>
                        <button
                          className="btn btn-sm btn-outline-success"
                          onClick={() => handlePostReportStatus(report.id, 'Reviewed')}
                        >
                          <i className="bi bi-check-circle me-1"></i>
                          Mark Reviewed
                        </button>
                        <button
                          className="btn btn-sm btn-outline-secondary"
                          onClick={() => handlePostReportStatus(report.id, 'Dismissed')}
                        >
                          <i className="bi bi-x-circle me-1"></i>
                          Dismiss
                        </button>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => handleDeletePost(report.post_id)}
                        >
                          <i className="bi bi-trash me-1"></i>
                          Delete Post
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Comment Reports */}
          {activeTab === 'comments' && (
            <div>
              {commentReports.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-check-circle display-1 text-success"></i>
                  <p className="text-muted mt-3">No pending comment reports</p>
                </div>
              ) : (
                commentReports.map((report) => (
                  <div key={report.id} className="card shadow-sm mb-3">
                    <div className="card-body">
                      <div className="d-flex justify-content-between align-items-start mb-3">
                        <div>
                          <h5 className="card-title mb-1">Comment #{report.comment_id}</h5>
                          <p className="text-muted small mb-0">
                            Reported {formatDate(report.created_at)} by User #{report.user_id}
                          </p>
                        </div>
                        <span className={`badge ${
                          report.status === 'Pending' ? 'bg-warning' :
                          report.status === 'Reviewed' ? 'bg-success' :
                          'bg-secondary'
                        }`}>
                          {report.status}
                        </span>
                      </div>

                      <div className="mb-3">
                        <strong>Reason:</strong>
                        <p className="mb-0">{report.reason}</p>
                      </div>

                      <div className="btn-group" role="group">
                        <button
                          className="btn btn-sm btn-outline-success"
                          onClick={() => handleCommentReportStatus(report.id, 'Reviewed')}
                        >
                          <i className="bi bi-check-circle me-1"></i>
                          Mark Reviewed
                        </button>
                        <button
                          className="btn btn-sm btn-outline-secondary"
                          onClick={() => handleCommentReportStatus(report.id, 'Dismissed')}
                        >
                          <i className="bi bi-x-circle me-1"></i>
                          Dismiss
                        </button>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => handleDeleteComment(report.comment_id)}
                        >
                          <i className="bi bi-trash me-1"></i>
                          Delete Comment
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Review;
