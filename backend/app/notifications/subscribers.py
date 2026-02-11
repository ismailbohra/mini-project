import app.utils.event_bus as event_bus_module
from app.config.database import AsyncSessionLocal
from app.notifications.repository import NotificationRepository
from app.utils.logging import get_logger
from app.websocket.manager import ws_manager

logger = get_logger(__name__)


async def on_comment_created(payload: dict):
    try:
        post_id = payload.get("post_id")
        comment_id = payload.get("comment_id")
        actor_id = payload.get("actor_id")
        post_author_id = payload.get("post_author_id")

        if actor_id == post_author_id:
            return

        async with AsyncSessionLocal() as session:
            repo = NotificationRepository(session)
            notification = await repo.create_notification(
                receiver_id=post_author_id,
                actor_id=actor_id,
                type="comment_created",
                post_id=post_id,
                comment_id=comment_id,
            )

            await ws_manager.send_to_user(
                post_author_id,
                {
                    "type": "notification",
                    "notification": {
                        "id": notification.id,
                        "receiver_id": notification.receiver_id,
                        "actor_id": notification.actor_id,
                        "actor_username": notification.actor.username,
                        "type": notification.type,
                        "post_id": notification.post_id,
                        "comment_id": notification.comment_id,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
            )
        logger.debug(f"Comment created notification sent for post {post_id}")
    except Exception as e:
        logger.exception(f"Error handling comment_created event: {e}")


async def on_comment_replied(payload: dict):
    try:
        post_id = payload.get("post_id")
        comment_id = payload.get("comment_id")
        actor_id = payload.get("actor_id")
        parent_author_id = payload.get("parent_author_id")

        if actor_id == parent_author_id:
            return

        async with AsyncSessionLocal() as session:
            repo = NotificationRepository(session)
            notification = await repo.create_notification(
                receiver_id=parent_author_id,
                actor_id=actor_id,
                type="comment_replied",
                post_id=post_id,
                comment_id=comment_id,
            )

            await ws_manager.send_to_user(
                parent_author_id,
                {
                    "type": "notification",
                    "notification": {
                        "id": notification.id,
                        "receiver_id": notification.receiver_id,
                        "actor_id": notification.actor_id,
                        "actor_username": notification.actor.username,
                        "type": notification.type,
                        "post_id": notification.post_id,
                        "comment_id": notification.comment_id,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
            )
        logger.debug(f"Comment replied notification sent for comment {comment_id}")
    except Exception as e:
        logger.exception(f"Error handling comment_replied event: {e}")


async def on_post_liked(payload: dict):
    try:
        logger.debug(f"on_post_liked triggered with payload: {payload}")
        post_id = payload.get("post_id")
        actor_id = payload.get("actor_id")
        post_author_id = payload.get("post_author_id")

        logger.debug(
            f"Post liked - post_id: {post_id}, actor: {actor_id}, author: {post_author_id}"
        )

        if actor_id == post_author_id:
            logger.debug("Skipping notification - user liked their own post")
            return

        async with AsyncSessionLocal() as session:
            repo = NotificationRepository(session)
            notification = await repo.create_notification(
                receiver_id=post_author_id,
                actor_id=actor_id,
                type="post_liked",
                post_id=post_id,
            )
            logger.debug(f"Notification created: {notification.id}")

            await ws_manager.send_to_user(
                post_author_id,
                {
                    "type": "notification",
                    "notification": {
                        "id": notification.id,
                        "receiver_id": notification.receiver_id,
                        "actor_id": notification.actor_id,
                        "actor_username": notification.actor.username,
                        "type": notification.type,
                        "post_id": notification.post_id,
                        "comment_id": notification.comment_id,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
            )
            logger.debug(f"Websocket message sent to user {post_author_id}")
    except Exception as e:
        logger.exception(f"Failed to handle post liked event: {e}")


async def on_comment_liked(payload: dict):
    try:
        logger.debug(f"on_comment_liked triggered with payload: {payload}")
        post_id = payload.get("post_id")
        comment_id = payload.get("comment_id")
        actor_id = payload.get("actor_id")
        comment_author_id = payload.get("comment_author_id")

        logger.debug(
            f"Comment liked - post_id: {post_id}, comment_id: {comment_id}, actor: {actor_id}, author: {comment_author_id}"
        )

        if actor_id == comment_author_id:
            logger.debug("Skipping notification - user liked their own comment")
            return

        async with AsyncSessionLocal() as session:
            repo = NotificationRepository(session)
            notification = await repo.create_notification(
                receiver_id=comment_author_id,
                actor_id=actor_id,
                type="comment_liked",
                post_id=post_id,
                comment_id=comment_id,
            )
            logger.debug(f"Notification created: {notification.id}")

            await ws_manager.send_to_user(
                comment_author_id,
                {
                    "type": "notification",
                    "notification": {
                        "id": notification.id,
                        "receiver_id": notification.receiver_id,
                        "actor_id": notification.actor_id,
                        "actor_username": notification.actor.username,
                        "type": notification.type,
                        "post_id": notification.post_id,
                        "comment_id": notification.comment_id,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
            )
            logger.debug(f"Websocket message sent to user {comment_author_id}")
    except Exception as e:
        logger.exception(f"Failed to handle comment liked event: {e}")


async def register_subscribers():
    if not event_bus_module.event_bus:
        logger.error("Event bus is not initialized, cannot register subscribers")
        return

    logger.info("Registering event subscribers...")
    await event_bus_module.event_bus.subscribe("comment.created", on_comment_created)
    logger.debug("Registered: comment.created")
    await event_bus_module.event_bus.subscribe("comment.replied", on_comment_replied)
    logger.debug("Registered: comment.replied")
    await event_bus_module.event_bus.subscribe("post.liked", on_post_liked)
    logger.debug("Registered: post.liked")
    await event_bus_module.event_bus.subscribe("comment.liked", on_comment_liked)
    logger.debug("Registered: comment.liked")
    logger.info(
        f"All subscribers registered. Total handlers: {len(event_bus_module.event_bus.handlers)}"
    )
