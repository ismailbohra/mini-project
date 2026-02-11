import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { formatDistanceToNow } from 'date-fns';
import moderatorService from '../services/moderatorService';

const Review = () => {
  const [activeTab, setActiveTab] = useState('posts');
  const [statusFilter, setStatusFilter] = useState('all'); // all, Pending, Reviewed, Dismissed
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

  const handleDeletePost = async (postId, reportId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;

    try {
      await moderatorService.deleteAnyPost(postId, reportId);
      toast.success('Post deleted successfully');
      loadReports();
    } catch (error) {
      toast.error('Failed to delete post');
    }
  };

  const handleDeleteComment = async (commentId, reportId) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) return;

    try {
      await moderatorService.deleteAnyComment(commentId, reportId);
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

  // Filter reports based on status
  const filteredPostReports = statusFilter === 'all' 
    ? postReports 
    : postReports.filter(r => r.status === statusFilter);
  
  const filteredCommentReports = statusFilter === 'all'
    ? commentReports
    : commentReports.filter(r => r.status === statusFilter);

  // Count reports by status
  const postStatusCounts = {
    all: postReports.length,
    Pending: postReports.filter(r => r.status === 'Pending').length,
    Reviewed: postReports.filter(r => r.status === 'Reviewed').length,
    Dismissed: postReports.filter(r => r.status === 'Dismissed').length,
    Deleted: postReports.filter(r => r.status === 'Deleted').length,
  };

  const commentStatusCounts = {
    all: commentReports.length,
    Pending: commentReports.filter(r => r.status === 'Pending').length,
    Reviewed: commentReports.filter(r => r.status === 'Reviewed').length,
    Dismissed: commentReports.filter(r => r.status === 'Dismissed').length,
    Deleted: commentReports.filter(r => r.status === 'Deleted').length,
  };

  return (
    <div className="container-fluid">
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
            {postStatusCounts.all > 0 && (
              <span className="badge bg-danger ms-2">{postStatusCounts.all}</span>
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
            {commentStatusCounts.all > 0 && (
              <span className="badge bg-danger ms-2">{commentStatusCounts.all}</span>
            )}
          </button>
        </li>
      </ul>

      {/* Status Filters */}
      <div className="btn-group mb-4" role="group">
        <button
          type="button"
          className={`btn btn-sm ${statusFilter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
          onClick={() => setStatusFilter('all')}
        >
          All ({activeTab === 'posts' ? postStatusCounts.all : commentStatusCounts.all})
        </button>
        <button
          type="button"
          className={`btn btn-sm ${statusFilter === 'Pending' ? 'btn-warning' : 'btn-outline-warning'}`}
          onClick={() => setStatusFilter('Pending')}
        >
          Pending ({activeTab === 'posts' ? postStatusCounts.Pending : commentStatusCounts.Pending})
        </button>
        <button
          type="button"
          className={`btn btn-sm ${statusFilter === 'Reviewed' ? 'btn-success' : 'btn-outline-success'}`}
          onClick={() => setStatusFilter('Reviewed')}
        >
          Reviewed ({activeTab === 'posts' ? postStatusCounts.Reviewed : commentStatusCounts.Reviewed})
        </button>
        <button
          type="button"
          className={`btn btn-sm ${statusFilter === 'Dismissed' ? 'btn-secondary' : 'btn-outline-secondary'}`}
          onClick={() => setStatusFilter('Dismissed')}
        >
          Dismissed ({activeTab === 'posts' ? postStatusCounts.Dismissed : commentStatusCounts.Dismissed})
        </button>
        <button
          type="button"
          className={`btn btn-sm ${statusFilter === 'Deleted' ? 'btn-danger' : 'btn-outline-danger'}`}
          onClick={() => setStatusFilter('Deleted')}
        >
          Deleted ({activeTab === 'posts' ? postStatusCounts.Deleted : commentStatusCounts.Deleted})
        </button>        <button
          type="button"
          className={`btn btn-sm ${statusFilter === 'Deleted' ? 'btn-danger' : 'btn-outline-danger'}`}
          onClick={() => setStatusFilter('Deleted')}
        >
          Deleted ({activeTab === 'posts' ? postStatusCounts.Deleted : commentStatusCounts.Deleted})
        </button>      </div>

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
              {filteredPostReports.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-check-circle display-1 text-success"></i>
                  <p className="text-muted mt-3">
                    No {statusFilter !== 'all' ? statusFilter.toLowerCase() : ''} post reports
                  </p>
                </div>
              ) : (
                filteredPostReports.map((report) => (
                  <div key={report.id} className="card shadow-sm mb-3">
                    <div className="card-body">
                      <div className="d-flex justify-content-between align-items-start mb-3">
                        <div className="flex-grow-1">
                          <h5 className="card-title mb-1">
                            <Link to={`/post/${report.post_id}`} className="text-decoration-none">
                              {report.post_title || `Post #${report.post_id}`}
                            </Link>
                          </h5>
                          <p className="text-muted small mb-0">
                            Reported {formatDate(report.created_at)} by {report.reporter_username || `User #${report.user_id}`}
                            {report.reviewed_at && (
                              <> • {report.status} {formatDate(report.reviewed_at)}</>
                            )}
                          </p>
                        </div>
                        <span className={`badge ${
                          report.status === 'Pending' ? 'bg-warning text-dark' :
                          report.status === 'Reviewed' ? 'bg-success' :
                          report.status === 'Deleted' ? 'bg-danger' :
                          'bg-secondary'
                        }`}>
                          {report.status}
                        </span>
                      </div>

                      <div className="mb-3">
                        <strong>Reason:</strong>
                        <p className="mb-0 mt-1">{report.reason}</p>
                      </div>

                      <div className="btn-group" role="group">
                        <Link
                          to={`/post/${report.post_id}`}
                          className="btn btn-sm btn-outline-primary"
                        >
                          <i className="bi bi-eye me-1"></i>
                          View Post
                        </Link>
                        {report.status === 'Pending' && (
                          <>
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
                              onClick={() => handleDeletePost(report.post_id, report.id)}
                            >
                              <i className="bi bi-trash me-1"></i>
                              Delete Post
                            </button>
                          </>
                        )}
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
              {filteredCommentReports.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-check-circle display-1 text-success"></i>
                  <p className="text-muted mt-3">
                    No {statusFilter !== 'all' ? statusFilter.toLowerCase() : ''} comment reports
                  </p>
                </div>
              ) : (
                filteredCommentReports.map((report) => (
                  <div key={report.id} className="card shadow-sm mb-3">
                    <div className="card-body">
                      <div className="d-flex justify-content-between align-items-start mb-3">
                        <div className="flex-grow-1">
                          <h5 className="card-title mb-1">
                            Comment #{report.comment_id}
                            {report.comment_author_username && (
                              <span className="text-muted fs-6"> by @{report.comment_author_username}</span>
                            )}
                          </h5>
                          <p className="text-muted small mb-0">
                            Reported {formatDate(report.created_at)} by {report.reporter_username || `User #${report.user_id}`}
                            {report.reviewed_at && (
                              <> • {report.status} {formatDate(report.reviewed_at)}</>
                            )}
                          </p>
                        </div>
                        <span className={`badge ${
                          report.status === 'Pending' ? 'bg-warning text-dark' :
                          report.status === 'Reviewed' ? 'bg-success' :
                          report.status === 'Deleted' ? 'bg-danger' :
                          'bg-secondary'
                        }`}>
                          {report.status}
                        </span>
                      </div>

                      {report.comment_title && (
                        <div className="mb-2">
                          <strong className="text-primary">{report.comment_title}</strong>
                        </div>
                      )}

                      {report.comment_description && (
                        <div className="mb-3 p-2 bg-light rounded">
                          <small className="text-muted d-block mb-1">Comment Content:</small>
                          <p className="mb-0">{report.comment_description}</p>
                        </div>
                      )}

                      <div className="mb-3">
                        <strong>Report Reason:</strong>
                        <p className="mb-0 mt-1">{report.reason}</p>
                      </div>

                      <div className="btn-group" role="group">
                        {report.status === 'Pending' && (
                          <>
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
                              onClick={() => handleDeleteComment(report.comment_id, report.id)}
                            >
                              <i className="bi bi-trash me-1"></i>
                              Delete Comment
                            </button>
                          </>
                        )}
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
