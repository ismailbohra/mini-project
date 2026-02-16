import { useState, useCallback, useEffect, useRef } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Hook to handle @mention autocomplete functionality
 * @param {string} text - The current text content
 * @param {number} cursorPosition - Current cursor position in the text
 * @returns {Object} - Autocomplete state and functions
 */
export const useMentionAutocomplete = (text, cursorPosition) => {
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [mentionQuery, setMentionQuery] = useState('');
  const [mentionStartPos, setMentionStartPos] = useState(null);
  const debounceRef = useRef(null);

  // Extract mention query at cursor position
  const extractMentionQuery = useCallback((text, cursorPos) => {
    if (!text || cursorPos === null) return null;

    // Find the last @ before cursor
    let lastAtPos = -1;
    for (let i = cursorPos - 1; i >= 0; i--) {
      if (text[i] === '@') {
        lastAtPos = i;
        break;
      }
      // Stop if we hit a space (means @ is for a different mention)
      if (text[i] === ' ' || text[i] === '\n') {
        break;
      }
    }

    if (lastAtPos === -1) return null;

    // Check if there's a space or start of text before @
    if (lastAtPos > 0 && !/[\s\n]/.test(text[lastAtPos - 1])) {
      return null;
    }

    // Extract the query between @ and cursor
    const query = text.substring(lastAtPos + 1, cursorPos);
    
    // Check if query contains spaces (invalid mention)
    if (query.includes(' ') || query.includes('\n')) {
      return null;
    }

    return {
      query: query.trim(),
      startPos: lastAtPos,
    };
  }, []);

  // Fetch user suggestions with debounce
  const fetchSuggestions = useCallback((query) => {
    // Clear any pending timeout
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    if (query.length < 1) {
      setSuggestions([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    
    debounceRef.current = setTimeout(async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_URL}/users/search/mentions`, {
          params: { q: query, limit: 10 },
          headers: { Authorization: `Bearer ${token}` },
        });
        setSuggestions(response.data);
      } catch (error) {
        console.error('Error fetching mention suggestions:', error);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    }, 300); // 300ms debounce
  }, []);

  // Update mention state when text or cursor changes
  useEffect(() => {
    const result = extractMentionQuery(text, cursorPosition);
    
    if (result) {
      setMentionQuery(result.query);
      setMentionStartPos(result.startPos);
      setShowSuggestions(true);
      fetchSuggestions(result.query);
    } else {
      setShowSuggestions(false);
      setSuggestions([]);
      setMentionQuery('');
      setMentionStartPos(null);
      setIsLoading(false);
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    }
  }, [text, cursorPosition, extractMentionQuery, fetchSuggestions]);

  // Insert selected mention
  const selectMention = useCallback((username) => {
    if (mentionStartPos === null) return text;

    // Replace from @ to cursor with @username followed by space
    const before = text.substring(0, mentionStartPos);
    const after = text.substring(cursorPosition);
    const newText = `${before}@${username} ${after}`;
    
    setShowSuggestions(false);
    setSuggestions([]);
    
    return {
      text: newText,
      cursorPosition: mentionStartPos + username.length + 2, // +2 for @ and space
    };
  }, [text, cursorPosition, mentionStartPos]);

  // Close suggestions
  const closeSuggestions = useCallback(() => {
    setShowSuggestions(false);
    setSuggestions([]);
  }, []);

  return {
    suggestions,
    isLoading,
    showSuggestions,
    mentionQuery,
    selectMention,
    closeSuggestions,
  };
};

/**
 * Extract mentioned usernames from text content
 * @param {string} content - Text content containing mentions
 * @returns {string[]} - Array of unique usernames mentioned
 */
export const extractMentions = (content) => {
  if (!content) return [];
  
  // Match @username pattern (alphanumeric, underscore, hyphen)
  const pattern = /@([a-zA-Z0-9_][a-zA-Z0-9_-]*)/g;
  const matches = content.match(pattern);
  
  if (!matches) return [];
  
  // Remove @ and deduplicate
  const usernames = matches.map(m => m.substring(1));
  return [...new Set(usernames)];
};
