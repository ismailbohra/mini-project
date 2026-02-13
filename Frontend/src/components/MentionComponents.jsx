import React from 'react';
import PropTypes from 'prop-types';

/**
 * Component to display mention autocomplete suggestions
 */
const MentionSuggestions = ({ suggestions, isLoading, onSelect, onClose }) => {
  if (!suggestions || suggestions.length === 0) {
    if (isLoading) {
      return (
        <div className="mention-suggestions loading">
          <div className="mention-suggestion-item">Loading...</div>
        </div>
      );
    }
    return null;
  }

  return (
    <div className="mention-suggestions">
      {suggestions.map((user) => (
        <div
          key={user.id}
          className="mention-suggestion-item"
          onClick={() => onSelect(user.username)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              onSelect(user.username);
            }
          }}
          role="button"
          tabIndex={0}
        >
          <div className="mention-suggestion-avatar">
            {user.profile_image ? (
              <img src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${user.profile_image}`} alt={user.username} />
            ) : (
              <div className="avatar-placeholder">
                {user.username.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <div className="mention-suggestion-username">@{user.username}</div>
        </div>
      ))}
    </div>
  );
};

MentionSuggestions.propTypes = {
  suggestions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      username: PropTypes.string.isRequired,
      profile_image: PropTypes.string,
    })
  ),
  isLoading: PropTypes.bool,
  onSelect: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};

MentionSuggestions.defaultProps = {
  suggestions: [],
  isLoading: false,
};

/**
 * Component to display mentioned users in a post/comment
 */
export const MentionedUsersList = ({ mentions }) => {
  if (!mentions || mentions.length === 0) return null;

  return (
    <div className="mentioned-users">
      <div className="mentioned-users-label">Mentioned:</div>
      <div className="mentioned-users-list">
        {mentions.map((user) => (
          <div key={user.id} className="mentioned-user-badge">
            {user.profile_image ? (
              <img 
                src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${user.profile_image}`} 
                alt={user.username}
                className="mentioned-user-avatar"
              />
            ) : (
              <div className="mentioned-user-avatar-placeholder">
                {user.username.charAt(0).toUpperCase()}
              </div>
            )}
            <span className="mentioned-user-name">@{user.username}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

MentionedUsersList.propTypes = {
  mentions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      username: PropTypes.string.isRequired,
      profile_image: PropTypes.string,
    })
  ),
};

MentionedUsersList.defaultProps = {
  mentions: [],
};

export default MentionSuggestions;
