import { useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';

export const useNotificationToast = () => {
  const { notifications, initialLoadComplete } = useSelector((state) => state.notifications);
  const previousCountRef = useRef(notifications.length);

  useEffect(() => {
    // Only show toasts after initial load is complete (i.e., only for websocket notifications)
    if (initialLoadComplete && notifications.length > previousCountRef.current) {
      const latestNotification = notifications[0];
      if (latestNotification && !latestNotification.is_read) {
        const actorName = latestNotification.actor_username || 'Someone';
        let message = '';
        
        switch (latestNotification.type) {
          case 'comment_created':
            message = `${actorName} commented on your post`;
            break;
          case 'comment_replied':
            message = `${actorName} replied to your comment`;
            break;
          case 'post_liked':
            message = `${actorName} liked your post`;
            break;
          case 'comment_liked':
            message = `${actorName} liked your comment`;
            break;
          case 'post_user_mentioned':
            message = `@${actorName} mentioned you in a post`;
            break;
          case 'comment_user_mentioned':
            message = `@${actorName} mentioned you in a comment`;
            break;
          default:
            message = 'New notification';
        }

        toast.info(message, {
          position: 'top-right',
          autoClose: 3000,
        });
      }
    }
    
    previousCountRef.current = notifications.length;
  }, [notifications]);
};
