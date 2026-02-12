import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import { formatDistanceToNow } from 'date-fns';
import commentService from '../services/commentService';

const CommentThread = ({ comment, postId, onUpdate, onDelete, level = 0 }) => {
  const { user } = useSelector((state) => state.auth);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState({ title: comment.title || 'Comment', description: comment.description });

  const canEdit = () => {
    if (!user) return false;
    return comment.author_id === user.id || user.role === 'Admin' || user.role === 'Moderator';
  };

  const canDelete = () => {
    if (!user) return false;
    return comment.author_id === user.id || user.role === 'Admin' || user.role === 'Moderator';
  };

  const canReport = () => {
    if (!user) return false;
    return comment.author_id != user.id || user.role === 'Admin' || user.role === 'Moderator';
  };

  const handleLike = async () => {
    try {
      if (comment.user_has_liked) {
        await commentService.unlikeComment(comment.id);
      } else {
        await commentService.likeComment(comment.id);
      }
      onUpdate();
    } catch (error) {
      toast.error('Failed to update like');
    }
  };

  const handleReply = async (e) => {
    e.preventDefault();
    if (!replyContent.trim()) return;

    try {
      await commentService.createComment({
        post_id: postId,
        title: 'Reply',
        description: replyContent,
        parent_comment_id: comment.id,
      });
      setReplyContent('');
      setShowReplyForm(false);
      onUpdate();
      toast.success('Reply posted!');
    } catch (error) {
      toast.error('Failed to post reply');
    }
  };

  const handleEdit = async (e) => {
    e.preventDefault();
    if (!editContent.description?.trim()) return;

    try {
      await commentService.updateComment(comment.id, editContent);
      setIsEditing(false);
      onUpdate();
      toast.success('Comment updated!');
    } catch (error) {
      toast.error('Failed to update comment');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this comment?')) return;

    try {
      await commentService.deleteComment(comment.id);
      onDelete(comment.id);
      toast.success('Comment deleted!');
    } catch (error) {
      toast.error('Failed to delete comment');
    }
  };

  const handleReport = async () => {
    const reason = prompt('Please provide a reason for reporting this comment:');
    if (!reason) return;

    try {
      await commentService.reportComment(comment.id, reason);
      toast.success('Comment reported successfully');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to report comment');
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
    <div className={`mb-3 ${level > 0 ? 'ms-4' : ''}`} style={{ borderLeft: level > 0 ? '2px solid #e0e0e0' : 'none', paddingLeft: level > 0 ? '15px' : '0' }}>
      <div className="card">
        <div className="card-body py-2">
          <div className="d-flex justify-content-between align-items-start mb-2">
            <div>
              <strong>{comment.author?.username || 'Unknown'}</strong>
              <small className="text-muted ms-2">{formatDate(comment.created_at)}</small>
            </div>
            {(canEdit() || canDelete() || canReport()) && (
              <div className="dropdown">
                <button
                  className="btn btn-sm btn-link text-muted p-0"
                  type="button"
                  data-bs-toggle="dropdown"
                >
                  <i className="bi bi-three-dots"></i>
                </button>
                <ul className="dropdown-menu dropdown-menu-end">
                  {canEdit() && (
                    <li>
                      <button className="dropdown-item" onClick={() => setIsEditing(true)}>
                        <i className="bi bi-pencil me-2"></i>Edit
                      </button>
                    </li>
                  )}
                  {canDelete() && (
                    <li>
                      <button className="dropdown-item text-danger" onClick={handleDelete}>
                        <i className="bi bi-trash me-2"></i>Delete
                      </button>
                    </li>
                  )}
                  {
                    canReport() && (
                      <li>
                        <button className="dropdown-item" onClick={handleReport}>
                          <i className="bi bi-flag me-2"></i>Report
                        </button>
                      </li>
                    )
                  }
                </ul>
              </div>
            )}
          </div>

          {isEditing ? (
            <form onSubmit={handleEdit}>
              <textarea
                className="form-control form-control-sm mb-2"
                value={editContent.description}
                onChange={(e) => setEditContent({ ...editContent, description: e.target.value })}
                rows="2"
              ></textarea>
              <button type="submit" className="btn btn-sm btn-primary me-2">
                Save
              </button>
              <button type="button" className="btn btn-sm btn-secondary" onClick={() => setIsEditing(false)}>
                Cancel
              </button>
            </form>
          ) : (
            <>
              <p className="mb-2">{comment.description}</p>
              <div className="d-flex gap-3">
                <button className="btn btn-sm btn-link p-0 text-decoration-none" onClick={handleLike}>
                  <i className={`bi ${comment.user_has_liked ? 'bi-heart-fill text-danger' : 'bi-heart'} me-1`}></i>
                  {comment.likes_count || 0}
                </button>
                <button
                  className="btn btn-sm btn-link p-0 text-decoration-none"
                  onClick={() => setShowReplyForm(!showReplyForm)}
                >
                  <i className="bi bi-reply me-1"></i>
                  Reply
                </button>
              </div>
            </>
          )}

          {showReplyForm && (
            <form onSubmit={handleReply} className="mt-2">
              <textarea
                className="form-control form-control-sm mb-2"
                placeholder="Write a reply..."
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                rows="2"
              ></textarea>
              <button type="submit" className="btn btn-sm btn-primary me-2">
                Post Reply
              </button>
              <button type="button" className="btn btn-sm btn-secondary" onClick={() => setShowReplyForm(false)}>
                Cancel
              </button>
            </form>
          )}
        </div>
      </div>

      {comment.replies && comment.replies.length > 0 && (
        <div className="mt-2">
          {comment.replies.map((reply) => (
            <CommentThread
              key={reply.id}
              comment={reply}
              postId={postId}
              onUpdate={onUpdate}
              onDelete={onDelete}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default CommentThread;
