import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PostCard from '../components/PostCard';
import FilterPanel from '../components/FilterPanel';
import Pagination from '../components/Pagination';
import { setLoading, setPosts, setError, setFilters, setPagination } from '../store/slices/postSlice';
import postService from '../services/postService';

const Home = () => {
  const dispatch = useDispatch();
  const { posts, loading, filters, pagination } = useSelector((state) => state.posts);
  const { user } = useSelector((state) => state.auth);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadPosts();
  }, [filters, pagination.page]);

  const loadPosts = async () => {
    dispatch(setLoading(true));
    try {
      const params = {
        skip: (pagination.page - 1) * pagination.limit,
        limit: pagination.limit,
      };

      // Add search parameter if exists
      if (filters.search) {
        params.search = filters.search;
      }

      // Add tags filter if exists
      if (filters.tags && filters.tags.length > 0) {
        params.tags = filters.tags;
      }

      // Add sort parameters
      if (filters.sortBy) {
        params.sort_by = filters.sortBy;
      }
      if (filters.sortOrder) {
        params.sort_order = filters.sortOrder;
      }

      const data = await postService.getPosts(params);
      dispatch(setPosts(data));
      // Calculate total pages based on response
      const totalPages = Math.ceil((data.length || 0) / pagination.limit);
      dispatch(setPagination({ total: data.length, totalPages }));
    } catch (error) {
      dispatch(setError(error.message));
      toast.error('Failed to load posts');
    }
  };

  const handleFilterChange = (newFilters) => {
    dispatch(setFilters(newFilters));
    dispatch(setPagination({ page: 1 }));
  };

  const handlePageChange = (page) => {
    dispatch(setPagination({ page }));
    window.scrollTo(0, 0);
  };

  const handleLike = async (postId) => {
    try {
      await postService.likePost(postId);
      loadPosts();
      toast.success('Post liked!');
    } catch (error) {
      toast.error('Failed to like post');
    }
  };

  const handleUnlike = async (postId) => {
    try {
      await postService.unlikePost(postId);
      loadPosts();
      toast.success('Post unliked!');
    } catch (error) {
      toast.error('Failed to unlike post');
    }
  };

  const handleDelete = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) {
      return;
    }
    try {
      await postService.deletePost(postId);
      loadPosts();
      toast.success('Post deleted successfully');
    } catch (error) {
      toast.error('Failed to delete post');
    }
  };

  const canEdit = (post) => {
    if (!user) return false;
    return post.author_id === user.id || user.role === 'Admin' || user.role === 'Moderator';
  };

  const canDelete = (post) => {
    if (!user) return false;
    return post.author_id === user.id || user.role === 'Admin' || user.role === 'Moderator';
  };

  return (
    <div className="container-fluid">
      <ToastContainer position="top-right" autoClose={3000} />
      
      <div className="row mb-3">
        <div className="col">
          <div className="d-flex justify-content-between align-items-center">
            <h2>
              <i className="bi bi-house me-2"></i>
              My Feed
            </h2>
            <button
              className="btn btn-outline-primary"
              onClick={() => setShowFilters(!showFilters)}
            >
              <i className="bi bi-funnel me-2"></i>
              Filters
            </button>
          </div>
        </div>
      </div>

      <FilterPanel
        filters={filters}
        onFilterChange={handleFilterChange}
        show={showFilters}
        onClose={() => setShowFilters(false)}
      />

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-5">
          <i className="bi bi-inbox display-1 text-muted"></i>
          <p className="text-muted mt-3">No posts found</p>
        </div>
      ) : (
        <>
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onLike={handleLike}
              onUnlike={handleUnlike}
              onDelete={handleDelete}
              canEdit={canEdit(post)}
              canDelete={canDelete(post)}
            />
          ))}
          
          <Pagination
            currentPage={pagination.page}
            totalPages={pagination.totalPages || 1}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  );
};

export default Home;
