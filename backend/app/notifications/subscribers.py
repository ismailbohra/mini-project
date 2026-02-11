import app.core.event_bus as event_bus_module
from app.config.database import AsyncSessionLocal
from app.notifications.repository import NotificationRepository
from app.websocket.manager import ws_manager


async def on_comment_created(payload: dict):
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


async def on_comment_replied(payload: dict):
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


async def on_post_liked(payload: dict):
    try:
        print(f"[DEBUG] on_post_liked triggered with payload: {payload}")
        post_id = payload.get("post_id")
        actor_id = payload.get("actor_id")
        post_author_id = payload.get("post_author_id")

        print(
            f"[DEBUG] Post liked - post_id: {post_id}, actor: {actor_id}, author: {post_author_id}"
        )

        if actor_id == post_author_id:
            print(f"[DEBUG] Skipping notification - user liked their own post")
            return

        async with AsyncSessionLocal() as session:
            repo = NotificationRepository(session)
            notification = await repo.create_notification(
                receiver_id=post_author_id,
                actor_id=actor_id,
                type="post_liked",
                post_id=post_id,
            )
            print(f"[DEBUG] Notification created: {notification.id}")

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
            print(f"[DEBUG] Websocket message sent to user {post_author_id}")
    except Exception as e:
        print(f"[ERROR] Failed to handle post liked event: {e}")
        import traceback

        traceback.print_exc()


async def on_comment_liked(payload: dict):
    try:
        print(f"[DEBUG] on_comment_liked triggered with payload: {payload}")
        post_id = payload.get("post_id")
        comment_id = payload.get("comment_id")
        actor_id = payload.get("actor_id")
        comment_author_id = payload.get("comment_author_id")

        print(
            f"[DEBUG] Comment liked - post_id: {post_id}, comment_id: {comment_id}, actor: {actor_id}, author: {comment_author_id}"
        )

        if actor_id == comment_author_id:
            print(f"[DEBUG] Skipping notification - user liked their own comment")
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
            print(f"[DEBUG] Notification created: {notification.id}")

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
            print(f"[DEBUG] Websocket message sent to user {comment_author_id}")
    except Exception as e:
        print(f"[ERROR] Failed to handle comment liked event: {e}")
        import traceback

        traceback.print_exc()


async def register_subscribers():
    if not event_bus_module.event_bus:
        print("[ERROR] Event bus is not initialized, cannot register subscribers")
        return

    print("[DEBUG] Registering event subscribers...")
    await event_bus_module.event_bus.subscribe("comment.created", on_comment_created)
    print("[DEBUG] Registered: comment.created")
    await event_bus_module.event_bus.subscribe("comment.replied", on_comment_replied)
    print("[DEBUG] Registered: comment.replied")
    await event_bus_module.event_bus.subscribe("post.liked", on_post_liked)
    print("[DEBUG] Registered: post.liked")
    await event_bus_module.event_bus.subscribe("comment.liked", on_comment_liked)
    print("[DEBUG] Registered: comment.liked")
    print(
        f"[DEBUG] All subscribers registered. Total handlers: {event_bus_module.event_bus.handlers}"
    )
