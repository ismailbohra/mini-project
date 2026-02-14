import React, { useState, useEffect } from 'react';
import postService from '../services/postService';

const FilterPanel = ({ filters, onFilterChange, show, onClose }) => {
  const [allTags, setAllTags] = useState([]);
  const [selectedTags, setSelectedTags] = useState(filters.tags || []);
  const [sortBy, setSortBy] = useState(filters.sortBy || 'created_at');
  const [sortOrder, setSortOrder] = useState(filters.sortOrder || 'desc');

  useEffect(() => {
    loadTags();
  }, []);

  // Sync local state with filters prop when it changes
  useEffect(() => {
    setSelectedTags(filters.tags || []);
    setSortBy(filters.sortBy || 'created_at');
    setSortOrder(filters.sortOrder || 'desc');
  }, [filters]);

  const loadTags = async () => {
    try {
      const tags = await postService.getAllTags();
      setAllTags(tags);
    } catch (error) {
      console.error('Failed to load tags', error);
    }
  };

  const handleTagToggle = (tagName) => {
    const newTags = selectedTags.includes(tagName)
      ? selectedTags.filter((t) => t !== tagName)
      : [...selectedTags, tagName];
    setSelectedTags(newTags);
  };

  const handleApply = () => {
    onFilterChange({
      tags: selectedTags,
      sortBy,
      sortOrder,
    });
    onClose();
  };

  const handleReset = () => {
    setSelectedTags([]);
    setSortBy('created_at');
    setSortOrder('desc');
    onFilterChange({
      tags: [],
      sortBy: 'created_at',
      sortOrder: 'desc',
    });
    onClose();
  };

  if (!show) return null;

  return (
    <div className="card mb-3 shadow-sm">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h6 className="mb-0">
          <i className="bi bi-funnel me-2"></i>
          Filters
        </h6>
        <button className="btn btn-sm btn-link text-decoration-none" onClick={onClose}>
          <i className="bi bi-x-lg"></i>
        </button>
      </div>
      <div className="card-body">
        {/* Tags */}
        <div className="mb-3">
          <label className="form-label fw-bold">Tags</label>
          <div className="d-flex flex-wrap gap-2">
            {allTags.map((tag) => (
              <div key={tag.id} className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id={`tag-${tag.id}`}
                  checked={selectedTags.includes(tag.name)}
                  onChange={() => handleTagToggle(tag.name)}
                />
                <label className="form-check-label" htmlFor={`tag-${tag.id}`}>
                  {tag.name}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Sort Options */}
        <div className="mb-3">
          <label className="form-label fw-bold">Sort By</label>
          <select
            className="form-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="created_at">Creation Date</option>
            <option value="updated_at">Last Updated</option>
          </select>
        </div>

        {/* Sort Order */}
        <div className="mb-3">
          <label className="form-label fw-bold">Order</label>
          <div>
            <div className="form-check form-check-inline">
              <input
                className="form-check-input"
                type="radio"
                name="sortOrder"
                id="desc"
                value="desc"
                checked={sortOrder === 'desc'}
                onChange={(e) => setSortOrder(e.target.value)}
              />
              <label className="form-check-label" htmlFor="desc">
                Descending
              </label>
            </div>
            <div className="form-check form-check-inline">
              <input
                className="form-check-input"
                type="radio"
                name="sortOrder"
                id="asc"
                value="asc"
                checked={sortOrder === 'asc'}
                onChange={(e) => setSortOrder(e.target.value)}
              />
              <label className="form-check-label" htmlFor="asc">
                Ascending
              </label>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="d-flex gap-2">
          <button className="btn btn-primary flex-grow-1" onClick={handleApply}>
            Apply Filters
          </button>
          <button className="btn btn-outline-secondary flex-grow-1" onClick={handleReset}>
            Reset
          </button>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;
