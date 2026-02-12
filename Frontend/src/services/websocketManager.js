import { store } from '../store';
import { addNotification, setConnected } from '../store/slices/notificationSlice';
import { updatePostLikesCount, updatePostCommentsCount, updateFullPost, deletePost } from '../store/slices/postSlice';
import { updateCommentLikesCount, deleteComment, addComment, addReply } from '../store/slices/commentSlice';

class WebSocketManager {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.userId = null;
    this.reconnectTimer = null;
    this.isIntentionallyClosed = false;
  }

  connect(userId, token) {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.userId = userId;
    this.isIntentionallyClosed = false;
    
    const wsUrl = `ws://localhost:8000/notifications/ws`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      store.dispatch(setConnected(true));
      
      this.ws.send(JSON.stringify({ user_id: userId }));
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('[WebSocket] Message received:', data);
        
        if (data.type === 'notification' && data.notification) {
          console.log('[WebSocket] Dispatching notification:', data.notification);
          store.dispatch(addNotification(data.notification));
        } else if (data.type === 'post_updated' && data.data) {
          console.log('[WebSocket] Post updated:', data.data);
          const { post_id, likes_count, comments_count, user_has_liked } = data.data;
          store.dispatch(updatePostLikesCount({
            postId: post_id,
            likesCount: likes_count,
            userHasLiked: user_has_liked,
          }));
          store.dispatch(updatePostCommentsCount({
            postId: post_id,
            commentsCount: comments_count,
          }));
        } else if (data.type === 'comment_updated' && data.data) {
          console.log('[WebSocket] Comment updated:', data.data);
          const { post_id, comment_id, likes_count, user_has_liked, post_comments_count } = data.data;
          store.dispatch(updateCommentLikesCount({
            commentId: comment_id,
            likesCount: likes_count,
            userHasLiked: user_has_liked,
          }));
          store.dispatch(updatePostCommentsCount({
            postId: post_id,
            commentsCount: post_comments_count,
          }));
        } else if (data.type === 'comment_deleted' && data.data) {
          console.log('[WebSocket] Comment deleted:', data.data);
          const { post_id, comment_id, post_comments_count } = data.data;
          store.dispatch(deleteComment(comment_id));
          store.dispatch(updatePostCommentsCount({
            postId: post_id,
            commentsCount: post_comments_count,
          }));
        } else if (data.type === 'post_fully_updated' && data.data) {
          console.log('[WebSocket] Post fully updated:', data.data);
          store.dispatch(updateFullPost(data.data));
        } else if (data.type === 'post_deleted' && data.data) {
          console.log('[WebSocket] Post deleted:', data.data);
          const { post_id } = data.data;
          store.dispatch(deletePost(post_id));
        } else if (data.type === 'comment_created' && data.data) {
          console.log('[WebSocket] Comment created:', data.data);
          const comment = data.data;
          // If it's a reply (has parent_comment_id), add it as a reply
          if (comment.parent_comment_id) {
            store.dispatch(addReply({
              parentCommentId: comment.parent_comment_id,
              reply: comment,
            }));
          } else {
            // Top-level comment
            store.dispatch(addComment(comment));
          }
          // Also update the post's comment count
          if (data.post_comments_count !== undefined) {
            store.dispatch(updatePostCommentsCount({
              postId: comment.post_id,
              commentsCount: data.post_comments_count,
            }));
          }
        } else {
          console.log('[WebSocket] Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      store.dispatch(setConnected(false));
      this.ws = null;

      if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
        this.reconnectTimer = setTimeout(() => {
          this.connect(userId, token);
        }, this.reconnectDelay);
      }
    };
  }

  disconnect() {
    this.isIntentionallyClosed = true;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.reconnectAttempts = 0;
    store.dispatch(setConnected(false));
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

export const wsManager = new WebSocketManager();
