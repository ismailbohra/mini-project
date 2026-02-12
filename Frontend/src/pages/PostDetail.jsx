import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { toast } from 'react-toastify';
import { formatDistanceToNow } from 'date-fns';
import CommentThread from '../components/CommentThread';
import { setCurrentPost, updatePost } from '../store/slices/postSlice';
import { setComments } from '../store/slices/commentSlice';
import postService from '../services/postService';
import commentService from '../services/commentService';

const PostDetail = () => {
  const { postId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { currentPost } = useSelector((state) => state.posts);
  const { comments: reduxComments } = useSelector((state) => state.comments);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({ title: '', description: '', tags: [] });
  const [detectedTags, setDetectedTags] = useState([]);
  const [postImage, setPostImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  useEffect(() => {
    loadPost();
    loadComments();
    return () => {
      dispatch(setCurrentPost(null));
    };
  }, [postId]);

  // Listen for post deletion and redirect to home
  useEffect(() => {
    if (!loading && currentPost === null && postId) {
      toast.info('This post has been deleted');
      navigate('/');
    }
  }, [currentPost, loading, postId, navigate]);

  useEffect(() => {
    if (isEditing) {
      const tags = extractTagsFromDescription(editData.description);
      setDetectedTags(tags);
    }
  }, [editData.description, isEditing]);

  const extractTagsFromDescription = (description) => {
    const tagPattern = /#(\w+)/g;
    const matches = description.matchAll(tagPattern);
    const extractedTags = [];

    for (const match of matches) {
      const tagName = match[1];
      if (!extractedTags.includes(tagName)) {
        extractedTags.push(tagName);
      }
    }

    return extractedTags;
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error('Please select a valid image file');
        return;
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error('Image size must be less than 10MB');
        return;
      }
      setPostImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const loadPost = async () => {
    try {
      const data = await postService.getPostById(postId);
      dispatch(setCurrentPost(data));
      setEditData({
        title: data.title,
        description: data.description,
        tags: data.tags?.map(t => t.name) || [],
      });
    } catch (error) {
      toast.error('Failed to load post');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const loadComments = async () => {
    try {
      const data = await commentService.getCommentsByPostId(postId);
      dispatch(setComments(data));
    } catch (error) {
      console.error('Failed to load comments', error);
    }
  };

  const handleCommentDeleted = (commentId) => {
    loadComments();
  };

  const handleLike = async () => {
    try {
      if (currentPost.user_has_liked) {
        await postService.unlikePost(postId);
      } else {
        await postService.likePost(postId);
      }
    } catch (error) {
      toast.error('Failed to update like');
    }
  };

  const handleReport = async () => {
    const reason = prompt('Please provide a reason for reporting this post:');
    if (!reason) return;

    try {
      await postService.reportPost(postId, reason);
      toast.success('Post reported successfully');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to report post');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;

    try {
      await postService.deletePost(postId);
      toast.success('Post deleted successfully');
      navigate('/my-posts');
    } catch (error) {
      toast.error('Failed to delete post');
    }
  };

  const handleEdit = async (e) => {
    e.preventDefault();
    
    // Extract tags from description
    const extractedTags = extractTagsFromDescription(editData.description);
    
    try {
      await postService.updatePost(postId, {
        ...editData,
        tags: extractedTags,
        image: postImage,
      });
      setIsEditing(false);
      setPostImage(null);
      setImagePreview(null);
      loadPost();
      toast.success('Post updated successfully');
    } catch (error) {
      toast.error('Failed to update post');
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await commentService.createComment({
        post_id: postId,
        title: 'Comment',
        description: newComment,
      });
      setNewComment('');
      loadComments();
      toast.success('Comment posted!');
    } catch (error) {
      toast.error('Failed to post comment');
    }
  };

  const canEdit = () => {
    if (!user || !currentPost) return false;
    return currentPost.author_id === user.id || user.role === 'Admin' || user.role === 'Moderator';
  };

  const canDelete = () => {
    if (!user || !currentPost) return false;
    return currentPost.author_id === user.id || user.role === 'Admin' || user.role === 'Moderator';
  };

  const formatDate = (dateString) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!currentPost) {
    return (
      <div className="text-center py-5">
        <p className="text-muted">Post not found</p>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card shadow-sm mb-4">
        <div className="card-body">
          {isEditing ? (
            <form onSubmit={handleEdit}>
              <div className="mb-3">
                <input
                  type="text"
                  className="form-control"
                  value={editData.title}
                  onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="editPostImage" className="form-label fw-bold">
                  Post Image
                </label>
                <input
                  type="file"
                  className="form-control"
                  id="editPostImage"
                  accept="image/*"
                  onChange={handleImageChange}
                />
                {currentPost.image_path && !imagePreview && (
                  <div className="mt-2">
                    <p className="text-muted mb-1">Current image:</p>
                    <img
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${currentPost.image_path}`}
                      alt="Current post"
                      className="img-thumbnail"
                      style={{ maxWidth: '100%', maxHeight: '300px', objectFit: 'contain' }}
                    />
                  </div>
                )}
                {imagePreview && (
                  <div className="mt-2">
                    <p className="text-muted mb-1">New image preview:</p>
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="img-thumbnail"
                      style={{ maxWidth: '100%', maxHeight: '300px', objectFit: 'contain' }}
                    />
                  </div>
                )}
                <small className="text-muted">Maximum file size: 10MB</small>
              </div>
              <div className="mb-3">
                <textarea
                  className="form-control"
                  rows="8"
                  value={editData.description}
                  onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                  required
                  placeholder="Write your post content... Use #tagname to mention tags"
                ></textarea>
                <small className="text-muted">
                  Use #tagname to mention tags (e.g., #AI, #React, #JavaScript)
                </small>
              </div>
              {detectedTags.length > 0 && (
                <div className="mb-3">
                  <label className="form-label fw-bold">Detected Tags:</label>
                  <div className="d-flex flex-wrap gap-2">
                    {detectedTags.map((tag, index) => (
                      <span key={index} className="badge bg-primary">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <button type="submit" className="btn btn-primary me-2">
                Save Changes
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setIsEditing(false)}>
                Cancel
              </button>
            </form>
          ) : (
            <>
              <div className="d-flex justify-content-between align-items-start mb-3">
                <h2>{currentPost.title}</h2>
                <div className="dropdown">
                  <button
                    className="btn btn-sm btn-outline-secondary"
                    type="button"
                    data-bs-toggle="dropdown"
                  >
                    <i className="bi bi-three-dots-vertical"></i>
                  </button>
                  <ul className="dropdown-menu dropdown-menu-end">
                    {canEdit() && (
                      <li>
                        <button className="dropdown-item" onClick={() => setIsEditing(true)}>
                          <i className="bi bi-pencil me-2"></i>Edit Post
                        </button>
                      </li>
                    )}
                    {canDelete() && (
                      <li>
                        <button className="dropdown-item text-danger" onClick={handleDelete}>
                          <i className="bi bi-trash me-2"></i>Delete Post
                        </button>
                      </li>
                    )}
                    <li>
                      <button className="dropdown-item" onClick={handleReport}>
                        <i className="bi bi-flag me-2"></i>Report Post
                      </button>
                    </li>
                  </ul>
                </div>
              </div>

              <p className="text-muted mb-3">
                {currentPost.author?.profile_image && (
                  <img
                    src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${currentPost.author.profile_image}`}
                    alt={currentPost.author.username}
                    className="rounded-circle me-2"
                    style={{ width: '30px', height: '30px', objectFit: 'cover' }}
                  />
                )}
                By <strong>{currentPost.author?.username || 'Unknown'}</strong> • {formatDate(currentPost.created_at)}
                {currentPost.updated_at !== currentPost.created_at && ' • (edited)'}
              </p>

              {currentPost.tags && currentPost.tags.length > 0 && (
                <div className="mb-3">
                  {currentPost.tags.map((tag) => (
                    <span key={tag.id} className="badge bg-secondary me-1">
                      {tag.name}
                    </span>
                  ))}
                </div>
              )}

              {currentPost.image_path && (
                <div className="mb-3 justify-content-center text-center">
                  <img
                    src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${currentPost.image_path}`}
                    alt={currentPost.title}
                    className="img-fluid rounded border"
                    style={{ maxWidth: '100%', maxHeight: '500px', objectFit: 'contain' }}
                  />
                </div>
              )}

              <div className="mb-3" style={{ whiteSpace: 'pre-wrap' }}>
                {currentPost.description}
              </div>

              <div className="d-flex gap-3">
                <button className="btn btn-sm btn-outline-primary" onClick={handleLike}>
                  <i className={`bi ${currentPost.user_has_liked ? 'bi-heart-fill' : 'bi-heart'} me-1`}></i>
                  {currentPost.likes_count || 0} Likes
                </button>
                <span className="btn btn-sm btn-outline-secondary">
                  <i className="bi bi-chat me-1"></i>
                  {currentPost.comments_count || 0} Comments
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Add Comment Form */}
      <div className="card shadow-sm mb-4">
        <div className="card-body">
          <h5 className="mb-3">Add a Comment</h5>
          <form onSubmit={handleAddComment}>
            <textarea
              className="form-control mb-2"
              placeholder="Write your comment..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              rows="3"
            ></textarea>
            <button type="submit" className="btn btn-primary">
              <i className="bi bi-send me-2"></i>
              Post Comment
            </button>
          </form>
        </div>
      </div>

      {/* Comments Section */}
      <div className="card shadow-sm">
        <div className="card-header">
          <h5 className="mb-0">Comments ({reduxComments.length})</h5>
        </div>
        <div className="card-body">
          {reduxComments.length === 0 ? (
            <p className="text-muted text-center">No comments yet. Be the first to comment!</p>
          ) : (
            reduxComments.map((comment) => (
              <CommentThread
                key={comment.id}
                comment={comment}
                postId={postId}
                onUpdate={loadComments}
                onDelete={loadComments}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default PostDetail;
