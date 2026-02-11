import React from 'react';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';

const PostCard = ({ post, onLike, onUnlike, onDelete, canEdit, canDelete }) => {
  const formatDate = (dateString) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="card mb-3 shadow-sm">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start">
          <Link to={`/post/${post.id}`} className="text-decoration-none text-dark">
            <h5 className="card-title">{post.title}</h5>
          </Link>
          {(canEdit || canDelete) && (
            <div className="dropdown">
              <button
                className="btn btn-sm btn-link text-muted"
                type="button"
                data-bs-toggle="dropdown"
              >
                <i className="bi bi-three-dots-vertical"></i>
              </button>
              <ul className="dropdown-menu">
                {canEdit && (
                  <li>
                    <Link className="dropdown-item" to={`/post/${post.id}`}>
                      <i className="bi bi-pencil me-2"></i>Edit
                    </Link>
                  </li>
                )}
                {canDelete && (
                  <li>
                    <button className="dropdown-item text-danger" onClick={() => onDelete(post.id)}>
                      <i className="bi bi-trash me-2"></i>Delete
                    </button>
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>

        <p className="card-text text-muted small mb-2">
          {post.author?.profile_image && (
            <img
              src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${post.author.profile_image}`}
              alt={post.author.username}
              className="rounded-circle me-1"
              style={{ width: '20px', height: '20px', objectFit: 'cover' }}
            />
          )}
          By <strong>{post.author?.username || 'Unknown'}</strong> • {formatDate(post.created_at)}
        </p>

        {post.image_path && (
          <div className="mb-2">
            <img
              src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${post.image_path}`}
              alt={post.title}
              className="img-fluid rounded"
              style={{ maxWidth: '100%', maxHeight: '200px', objectFit: 'cover' }}
            />
          </div>
        )}

        <p className="card-text">
          {post.description?.substring(0, 150)}
          {post.description?.length > 150 ? '...' : ''}
        </p>

        {post.tags && post.tags.length > 0 && (
          <div className="mb-2">
            {post.tags.map((tag) => (
              <span key={tag.id} className="badge bg-secondary me-1">
                {tag.name}
              </span>
            ))}
          </div>
        )}

        <div className="d-flex gap-3">
          <button 
            className="btn btn-sm btn-outline-primary"
            onClick={() => post.user_has_liked ? onUnlike(post.id) : onLike(post.id)}
          >
            <i className={`bi ${post.user_has_liked ? 'bi-heart-fill' : 'bi-heart'} me-1`}></i>
            {post.likes_count || 0}
          </button>
          <Link to={`/post/${post.id}`} className="btn btn-sm btn-outline-secondary">
            <i className="bi bi-chat me-1"></i>
            {post.comments_count || 0}
            -Comments
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PostCard;
