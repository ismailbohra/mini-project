import api from './api';

export const postService = {
  // Get all posts with search, filter, and sort
  getPosts: async (params = {}) => {
    const response = await api.get('/posts', { params });
    return response.data;
  },

  // Get search suggestions
  getSearchSuggestions: async (search) => {
    if (!search || search.length < 2) {
      return [];
    }
    const response = await api.get('/posts/search/suggestions', {
      params: { search },
    });
    return response.data;
  },

  // Get post by ID
  getPostById: async (postId) => {
    const response = await api.get(`/posts/${postId}`);
    return response.data;
  },

  // Get my posts
  getMyPosts: async (params = {}) => {
    const response = await api.get('/posts/user/me', { params });
    return response.data;
  },

  // Create post
  createPost: async (postData) => {
    const formData = new FormData();
    formData.append('title', postData.title);
    formData.append('description', postData.description);
    formData.append('tags', JSON.stringify(postData.tags || []));
    if (postData.image) {
      formData.append('image', postData.image);
    }
    const response = await api.post('/posts', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Update post
  updatePost: async (postId, postData) => {
    const formData = new FormData();
    if (postData.title !== undefined) {
      formData.append('title', postData.title);
    }
    if (postData.description !== undefined) {
      formData.append('description', postData.description);
    }
    if (postData.tags !== undefined) {
      formData.append('tags', JSON.stringify(postData.tags));
    }
    if (postData.image) {
      formData.append('image', postData.image);
    }
    const response = await api.put(`/posts/${postId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Delete post
  deletePost: async (postId) => {
    await api.delete(`/posts/${postId}`);
  },

  // Like/Unlike post
  likePost: async (postId) => {
    const response = await api.post(`/posts/${postId}/like`);
    return response.data;
  },

  unlikePost: async (postId) => {
    await api.delete(`/posts/${postId}/like`);
  },

  // Get post likes count
  getPostLikesCount: async (postId) => {
    const response = await api.get(`/posts/${postId}/likes/count`);
    return response.data;
  },

  // Report post
  reportPost: async (postId, reason) => {
    const response = await api.post(`/posts/${postId}/report`, null, {
      params: { reason },
    });
    return response.data;
  },

  // Get all tags
  getAllTags: async () => {
    const response = await api.get('/posts/tags');
    return response.data;
  },
};

export default postService;
