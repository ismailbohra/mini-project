import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useMentionAutocomplete, extractMentions } from '../hooks/useMentionAutocomplete';
import MentionSuggestions, { MentionedUsersList } from './MentionComponents';
import './MentionStyles.css';

/**
 * Example component showing how to integrate mentions into a post/comment form
 * 
 * Usage:
 * <MentionTextArea
 *   value={description}
 *   onChange={setDescription}
 *   placeholder="Write your post... Use @ to mention users"
 *   onMentionsChange={(mentions) => console.log('Mentioned users:', mentions)}
 * />
 */
const MentionTextArea = ({ 
  value, 
  onChange, 
  placeholder,
  onMentionsChange,
  className,
  rows = 4,
}) => {
  const [cursorPosition, setCursorPosition] = useState(0);
  const textAreaRef = useRef(null);
  const [mentionedUsernames, setMentionedUsernames] = useState([]);

  const {
    suggestions,
    isLoading,
    showSuggestions,
    selectMention,
    closeSuggestions,
  } = useMentionAutocomplete(value, cursorPosition);

  // Update mentioned usernames when content changes
  useEffect(() => {
    const mentions = extractMentions(value);
    setMentionedUsernames(mentions);
    if (onMentionsChange) {
      onMentionsChange(mentions);
    }
  }, [value, onMentionsChange]);

  // Handle text area change
  const handleChange = (e) => {
    onChange(e.target.value);
    setCursorPosition(e.target.selectionStart);
  };

  // Update cursor position on selection change
  const handleSelectionChange = (e) => {
    setCursorPosition(e.target.selectionStart);
  };

  // Handle mention selection
  const handleMentionSelect = (username) => {
    const result = selectMention(username);
    onChange(result.text);
    
    // Set cursor position after mention
    setTimeout(() => {
      if (textAreaRef.current) {
        textAreaRef.current.focus();
        textAreaRef.current.setSelectionRange(
          result.cursorPosition,
          result.cursorPosition
        );
        setCursorPosition(result.cursorPosition);
      }
    }, 0);
  };

  // Handle keyboard navigation in suggestions
  const handleKeyDown = (e) => {
    if (showSuggestions && suggestions.length > 0) {
      if (e.key === 'Escape') {
        closeSuggestions();
        e.preventDefault();
      }
      // You can add arrow key navigation here if needed
    }
  };

  return (
    <div className="mention-textarea-container">
      <div className="mention-input-container">
        <textarea
          ref={textAreaRef}
          value={value}
          onChange={handleChange}
          onSelect={handleSelectionChange}
          onClick={handleSelectionChange}
          onKeyUp={handleSelectionChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={`mention-textarea ${className || ''}`}
          rows={rows}
        />
        
        {showSuggestions && (
          <MentionSuggestions
            suggestions={suggestions}
            isLoading={isLoading}
            onSelect={handleMentionSelect}
            onClose={closeSuggestions}
          />
        )}
      </div>

      {mentionedUsernames.length > 0 && (
        <div className="mentioned-usernames-preview">
          <span className="preview-label">Mentioning:</span>
          <div className="preview-badges">
            {mentionedUsernames.map((username, index) => (
              <span key={index} className="username-badge">
                @{username}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

MentionTextArea.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  onMentionsChange: PropTypes.func,
  className: PropTypes.string,
  rows: PropTypes.number,
};

MentionTextArea.defaultProps = {
  placeholder: 'Write something... Use @ to mention users',
  onMentionsChange: null,
  className: '',
  rows: 4,
};

export default MentionTextArea;
