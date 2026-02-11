import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import postService from '../services/postService';

const CreatePost = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [allTags, setAllTags] = useState([]);
  const [detectedTags, setDetectedTags] = useState([]);
  const [postImage, setPostImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
  });

  useEffect(() => {
    loadTags();
  }, []);

  useEffect(() => {
    const tags = extractTagsFromDescription(formData.description);
    setDetectedTags(tags);
  }, [formData.description]);

  const loadTags = async () => {
    try {
      const tags = await postService.getAllTags();
      setAllTags(tags);
    } catch (error) {
      console.error('Failed to load tags', error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
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
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Extract tags from description
    const extractedTags = extractTagsFromDescription(formData.description);

    try {
      await postService.createPost({
        title: formData.title,
        description: formData.description,
        tags: extractedTags,
        image: postImage,
      });
      toast.success('Post created successfully!');
      setTimeout(() => {
        navigate('/my-posts');
      }, 1000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  

  return (
    <div className="container">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-header bg-primary text-white">
              <h4 className="mb-0">
                <i className="bi bi-plus-circle me-2"></i>
                Create New Post
              </h4>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="title" className="form-label fw-bold">
                    Title <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    required
                    placeholder="Enter post title"
                  />
                </div>

                <div className="mb-3">
                  <label htmlFor="postImage" className="form-label fw-bold">
                    Post Image (Optional)
                  </label>
                  <input
                    type="file"
                    className="form-control"
                    id="postImage"
                    accept="image/*"
                    onChange={handleImageChange}
                  />
                  {imagePreview && (
                    <div className="mt-2">
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
                  <label htmlFor="description" className="form-label fw-bold">
                    Content <span className="text-danger">*</span>
                  </label>
                  <textarea
                    className="form-control"
                    id="description"
                    name="description"
                    rows="10"
                    value={formData.description}
                    onChange={handleChange}
                    required
                    placeholder="Write your post content here... Use #tagname to mention tags"
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

                <div className="d-flex gap-2">
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Creating...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-circle me-2"></i>
                        Create Post
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => navigate(-1)}
                    disabled={loading}
                  >
                    <i className="bi bi-x-circle me-2"></i>
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreatePost;