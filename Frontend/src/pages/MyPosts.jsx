import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import PostCard from '../components/PostCard';
import FilterPanel from '../components/FilterPanel';
import Pagination from '../components/Pagination';
import { setLoading, setPosts, setError, setFilters, setPagination } from '../store/slices/postSlice';
import postService from '../services/postService';

const MyPosts = () => {
  const dispatch = useDispatch();
  const { posts, loading, filters, pagination } = useSelector((state) => state.posts);
  const { user } = useSelector((state) => state.auth);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadMyPosts();
  }, [filters, pagination.page]);

  const loadMyPosts = async () => {
    dispatch(setLoading(true));
    try {
      const params = {
        skip: (pagination.page - 1) * pagination.limit,
        limit: pagination.limit,
        ...filters,
      };
      const data = await postService.getMyPosts(params);
      dispatch(setPosts(data.posts));
      const totalPages = Math.ceil((data.total || 0) / pagination.limit);
      dispatch(setPagination({ total: data.total, totalPages }));
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
      loadMyPosts();
      toast.success('Post liked!');
    } catch (error) {
      toast.error('Failed to like post');
    }
  };

  const handleUnlike = async (postId) => {
    try {
      await postService.unlikePost(postId);
      loadMyPosts();
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
      loadMyPosts();
      toast.success('Post deleted successfully');
    } catch (error) {
      toast.error('Failed to delete post');
    }
  };

  return (
    <div className="container-fluid">
      <div className="row mb-3">
        <div className="col">
          <div className="d-flex justify-content-between align-items-center">
            <h2>
              <i className="bi bi-file-text me-2"></i>
              My Posts
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
          <p className="text-muted mt-3">You haven't created any posts yet</p>
        </div>
      ) : (
        <>
          <div className='d-flex justify-content-end mb-3'>
            <Pagination
              currentPage={pagination.page}
              totalPages={pagination.totalPages || 1}
              onPageChange={handlePageChange}
            />
          </div>
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onLike={handleLike}
              onUnlike={handleUnlike}
              onDelete={handleDelete}
              canEdit={true}
              canDelete={true}
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

export default MyPosts;
