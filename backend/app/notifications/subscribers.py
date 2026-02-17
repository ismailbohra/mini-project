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

        # Send notification to post author if not the same as actor
        if actor_id != post_author_id:
            async with AsyncSessionLocal() as session:
                repo = NotificationRepository(session)
                notification = await repo.create_notification(
                    receiver_id=post_author_id,
                    actor_id=actor_id,
                    type="comment_created",
                    post_id=post_id,
                    comment_id=comment_id,
                )

                if notification:
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

        # Broadcast comment to all connected users for real-time updates
        from app.comments.repository import CommentRepository
        from app.posts.repository import PostRepository

        async with AsyncSessionLocal() as session:
            comment_repo = CommentRepository(session)
            post_repo = PostRepository(session)
            comment = await comment_repo.get_comment_by_id(comment_id)
            if comment:
                likes_count = await comment_repo.get_comment_likes_count(comment_id)
                post_comments_count = await post_repo.get_post_comments_count(post_id)

                comment_data = {
                    "id": comment.id,
                    "author_id": comment.author_id,
                    "author": {
                        "id": comment.author.id,
                        "username": comment.author.username,
                        "email": comment.author.email,
                    }
                    if comment.author
                    else None,
                    "post_id": comment.post_id,
                    "title": comment.title,
                    "description": comment.description,
                    "parent_comment_id": comment.parent_comment_id,
                    "created_at": comment.created_at.isoformat(),
                    "updated_at": comment.updated_at.isoformat(),
                    "likes_count": likes_count,
                    "user_has_liked": False,
                    "replies": [],
                }

                for user_id in ws_manager.active_connections.keys():
                    # Check if user has liked
                    user_like = await comment_repo.get_comment_like(user_id, comment_id)
                    comment_data_copy = comment_data.copy()
                    comment_data_copy["user_has_liked"] = user_like is not None

                    await ws_manager.send_to_user(
                        user_id,
                        {
                            "type": "comment_created",
                            "data": comment_data_copy,
                            "post_comments_count": post_comments_count,
                        },
                    )

        logger.debug(
            f"Comment created notification and broadcast sent for post {post_id}"
        )
    except Exception as e:
        logger.exception(f"Error handling comment_created event: {e}")


async def on_comment_replied(payload: dict):
    try:
        post_id = payload.get("post_id")
        comment_id = payload.get("comment_id")
        actor_id = payload.get("actor_id")
        parent_author_id = payload.get("parent_author_id")

        # Send notification to parent comment author if not the same as actor
        if actor_id != parent_author_id:
            async with AsyncSessionLocal() as session:
                repo = NotificationRepository(session)
                notification = await repo.create_notification(
                    receiver_id=parent_author_id,
                    actor_id=actor_id,
                    type="comment_replied",
                    post_id=post_id,
                    comment_id=comment_id,
                )

                if notification:
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

        # Broadcast reply to all connected users for real-time updates
        from app.comments.repository import CommentRepository
        from app.posts.repository import PostRepository

        async with AsyncSessionLocal() as session:
            comment_repo = CommentRepository(session)
            post_repo = PostRepository(session)
            comment = await comment_repo.get_comment_by_id(comment_id)
            if comment:
                likes_count = await comment_repo.get_comment_likes_count(comment_id)
                post_comments_count = await post_repo.get_post_comments_count(post_id)

                comment_data = {
                    "id": comment.id,
                    "author_id": comment.author_id,
                    "author": {
                        "id": comment.author.id,
                        "username": comment.author.username,
                        "email": comment.author.email,
                    }
                    if comment.author
                    else None,
                    "post_id": comment.post_id,
                    "title": comment.title,
                    "description": comment.description,
                    "parent_comment_id": comment.parent_comment_id,
                    "created_at": comment.created_at.isoformat(),
                    "updated_at": comment.updated_at.isoformat(),
                    "likes_count": likes_count,
                    "user_has_liked": False,
                    "replies": [],
                }

                for user_id in ws_manager.active_connections.keys():
                    # Check if user has liked
                    user_like = await comment_repo.get_comment_like(user_id, comment_id)
                    comment_data_copy = comment_data.copy()
                    comment_data_copy["user_has_liked"] = user_like is not None

                    await ws_manager.send_to_user(
                        user_id,
                        {
                            "type": "comment_created",
                            "data": comment_data_copy,
                            "post_comments_count": post_comments_count,
                        },
                    )

        logger.debug(
            f"Comment replied notification and broadcast sent for comment {comment_id}"
        )
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

            if not notification:
                logger.debug(
                    "Duplicate notification prevented - skipping websocket send"
                )
                return

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

            if not notification:
                logger.debug(
                    "Duplicate notification prevented - skipping websocket send"
                )
                return

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


async def on_post_state_updated(payload: dict):
    try:
        post_id = payload.get("post_id")
        payload.get("actor_id")

        from app.config.database import AsyncSessionLocal
        from app.posts.repository import PostRepository

        async with AsyncSessionLocal() as session:
            post_repo = PostRepository(session)
            post = await post_repo.get_post_by_id(post_id)
            if not post:
                return

            likes_count = await post_repo.get_post_likes_count(post_id)
            comments_count = await post_repo.get_post_comments_count(post_id)

            for user_id in ws_manager.active_connections.keys():
                existing_like = await post_repo.get_post_like(user_id, post_id)
                user_has_liked = existing_like is not None

                await ws_manager.send_to_user(
                    user_id,
                    {
                        "type": "post_updated",
                        "data": {
                            "post_id": post_id,
                            "likes_count": likes_count,
                            "comments_count": comments_count,
                            "user_has_liked": user_has_liked,
                        },
                    },
                )
        logger.debug(f"Post state update broadcast for post {post_id}")
    except Exception as e:
        logger.exception(f"Error handling post.state.updated event: {e}")


async def on_comment_state_updated(payload: dict):
    try:
        post_id = payload.get("post_id")
        comment_id = payload.get("comment_id")

        from app.comments.repository import CommentRepository
        from app.config.database import AsyncSessionLocal
        from app.posts.repository import PostRepository

        async with AsyncSessionLocal() as session:
            comment_repo = CommentRepository(session)
            post_repo = PostRepository(session)

            comment = await comment_repo.get_comment_by_id(comment_id)
            if not comment:
                return

            likes_count = await comment_repo.get_comment_likes_count(comment_id)
            comments_count = await post_repo.get_post_comments_count(post_id)

            for user_id in ws_manager.active_connections.keys():
                comment_like = await comment_repo.get_comment_like(user_id, comment_id)
                user_has_liked = comment_like is not None

                await ws_manager.send_to_user(
                    user_id,
                    {
                        "type": "comment_updated",
                        "data": {
                            "post_id": post_id,
                            "comment_id": comment_id,
                            "likes_count": likes_count,
                            "user_has_liked": user_has_liked,
                            "post_comments_count": comments_count,
                        },
                    },
                )
        logger.debug(f"Comment state update broadcast for comment {comment_id}")
    except Exception as e:
        logger.exception(f"Error handling comment.state.updated event: {e}")


async def on_comment_deleted(payload: dict):
    try:
        post_id = payload.get("post_id")
        comment_id = payload.get("comment_id")

        from app.config.database import AsyncSessionLocal
        from app.posts.repository import PostRepository

        async with AsyncSessionLocal() as session:
            post_repo = PostRepository(session)
            comments_count = await post_repo.get_post_comments_count(post_id)

            for user_id in ws_manager.active_connections.keys():
                await ws_manager.send_to_user(
                    user_id,
                    {
                        "type": "comment_deleted",
                        "data": {
                            "post_id": post_id,
                            "comment_id": comment_id,
                            "post_comments_count": comments_count,
                        },
                    },
                )
        logger.debug(f"Comment deletion broadcast for comment {comment_id}")
    except Exception as e:
        logger.exception(f"Error handling comment.deleted event: {e}")


async def on_post_deleted(payload: dict):
    try:
        post_id = payload.get("post_id")
        actor_id = payload.get("actor_id")

        # Broadcast post deletion to all connected users
        for user_id in ws_manager.active_connections.keys():
            await ws_manager.send_to_user(
                user_id,
                {
                    "type": "post_deleted",
                    "data": {
                        "post_id": post_id,
                        "actor_id": actor_id,
                    },
                },
            )
        logger.debug(f"Post deletion broadcast for post {post_id}")
    except Exception as e:
        logger.exception(f"Error handling post.deleted event: {e}")


async def on_post_added(payload: dict):
    try:
        post_id = payload.get("post_id")

        for user_id in ws_manager.active_connections.keys():
            await ws_manager.send_to_user(
                user_id,
                {
                    "type": "new_post_added",
                    "data": {
                        "post_id": post_id,
                    },
                },
            )
        logger.info(f"New post broadcast for post {post_id}")
    except Exception as e:
        logger.exception(f"Error handling post.new_post_added event: {e}")


async def on_post_updated(payload: dict):
    try:
        post_id = payload.get("post_id")
        payload.get("actor_id")

        from app.config.database import AsyncSessionLocal
        from app.posts.repository import PostRepository

        async with AsyncSessionLocal() as session:
            post_repo = PostRepository(session)
            post = await post_repo.get_post_by_id(post_id)
            if not post:
                return

            from app.posts.schema import TagResponse

            tags = [TagResponse(id=pt.tag.id, name=pt.tag.name) for pt in post.tags]

            author_obj = None
            if post.author:
                author_obj = {
                    "id": post.author.id,
                    "username": post.author.username,
                    "email": post.author.email,
                    "profile_image": post.author.profile_image,
                }

            likes_count = await post_repo.get_post_likes_count(post_id)
            comments_count = await post_repo.get_post_comments_count(post_id)

            for user_id in ws_manager.active_connections.keys():
                existing_like = await post_repo.get_post_like(user_id, post_id)
                user_has_liked = existing_like is not None

                await ws_manager.send_to_user(
                    user_id,
                    {
                        "type": "post_fully_updated",
                        "data": {
                            "id": post_id,
                            "author_id": post.author_id,
                            "author": author_obj,
                            "title": post.title,
                            "description": post.description,
                            "tags": [{"id": t.id, "name": t.name} for t in tags],
                            "created_at": post.created_at.isoformat(),
                            "updated_at": post.updated_at.isoformat(),
                            "likes_count": likes_count,
                            "comments_count": comments_count,
                            "user_has_liked": user_has_liked,
                            "image_path": post.image_path,
                        },
                    },
                )
        logger.debug(f"Post update broadcast for post {post_id}")
    except Exception as e:
        logger.exception(f"Error handling post.updated event: {e}")


async def on_post_user_mentioned(payload: dict):
    """Handle post mention notifications."""
    try:
        post_id = payload.get("post_id")
        mentioned_user_id = payload.get("mentioned_user_id")
        actor_id = payload.get("actor_id")
        actor_username = payload.get("actor_username")
        mentioned_username = payload.get("mentioned_username")

        logger.debug(
            f"Post mention - post_id: {post_id}, mentioned: {mentioned_username} (ID: {mentioned_user_id}), "
            f"actor: {actor_username} (ID: {actor_id})"
        )

        # Don't send notification if user mentioned themselves (shouldn't happen, but safe check)
        if actor_id == mentioned_user_id:
            logger.debug("Skipping notification - user mentioned themselves")
            return

        async with AsyncSessionLocal() as session:
            repo = NotificationRepository(session)
            notification = await repo.create_notification(
                receiver_id=mentioned_user_id,
                actor_id=actor_id,
                type="post_user_mentioned",
                post_id=post_id,
            )

            if not notification:
                logger.debug(
                    "Duplicate notification prevented - skipping websocket send"
                )
                return

            logger.debug(f"Mention notification created: {notification.id}")

            # Send WebSocket notification
            await ws_manager.send_to_user(
                mentioned_user_id,
                {
                    "type": "notification",
                    "notification": {
                        "id": notification.id,
                        "receiver_id": notification.receiver_id,
                        "actor_id": notification.actor_id,
                        "actor_username": actor_username,
                        "type": notification.type,
                        "post_id": notification.post_id,
                        "comment_id": notification.comment_id,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
            )
            logger.debug(f"Websocket notification sent to user {mentioned_user_id}")
    except Exception as e:
        logger.exception(f"Failed to handle post mention event: {e}")


async def on_comment_user_mentioned(payload: dict):
    """Handle comment mention notifications."""
    try:
        post_id = payload.get("post_id")
        comment_id = payload.get("comment_id")
        mentioned_user_id = payload.get("mentioned_user_id")
        actor_id = payload.get("actor_id")
        actor_username = payload.get("actor_username")
        mentioned_username = payload.get("mentioned_username")

        logger.debug(
            f"Comment mention - post_id: {post_id}, comment_id: {comment_id}, "
            f"mentioned: {mentioned_username} (ID: {mentioned_user_id}), actor: {actor_username} (ID: {actor_id})"
        )

        # Don't send notification if user mentioned themselves (shouldn't happen, but safe check)
        if actor_id == mentioned_user_id:
            logger.debug("Skipping notification - user mentioned themselves")
            return

        async with AsyncSessionLocal() as session:
            repo = NotificationRepository(session)
            notification = await repo.create_notification(
                receiver_id=mentioned_user_id,
                actor_id=actor_id,
                type="comment_user_mentioned",
                post_id=post_id,
                comment_id=comment_id,
            )

            if not notification:
                logger.debug(
                    "Duplicate notification prevented - skipping websocket send"
                )
                return

            logger.debug(f"Mention notification created: {notification.id}")

            # Send WebSocket notification
            await ws_manager.send_to_user(
                mentioned_user_id,
                {
                    "type": "notification",
                    "notification": {
                        "id": notification.id,
                        "receiver_id": notification.receiver_id,
                        "actor_id": notification.actor_id,
                        "actor_username": actor_username,
                        "type": notification.type,
                        "post_id": notification.post_id,
                        "comment_id": notification.comment_id,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
            )
            logger.debug(f"Websocket notification sent to user {mentioned_user_id}")
    except Exception as e:
        logger.exception(f"Failed to handle comment mention event: {e}")


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
    await event_bus_module.event_bus.subscribe(
        "post.state.updated", on_post_state_updated
    )
    logger.debug("Registered: post.state.updated")
    await event_bus_module.event_bus.subscribe(
        "comment.state.updated", on_comment_state_updated
    )
    logger.debug("Registered: comment.state.updated")
    await event_bus_module.event_bus.subscribe("comment.deleted", on_comment_deleted)
    logger.debug("Registered: comment.deleted")
    await event_bus_module.event_bus.subscribe("post.deleted", on_post_deleted)
    logger.debug("Registered: post.deleted")
    await event_bus_module.event_bus.subscribe("post.updated", on_post_updated)

    logger.debug("Registered: post.Added")
    await event_bus_module.event_bus.subscribe("post.new_post_added", on_post_added)

    logger.debug("Registered: post.updated")

    await event_bus_module.event_bus.subscribe(
        "post.user_mentioned", on_post_user_mentioned
    )
    logger.debug("Registered: post.user_mentioned")

    await event_bus_module.event_bus.subscribe(
        "comment.user_mentioned", on_comment_user_mentioned
    )
    logger.debug("Registered: comment.user_mentioned")

    logger.info(
        f"All subscribers registered. Total handlers: {len(event_bus_module.event_bus.handlers)}"
    )
