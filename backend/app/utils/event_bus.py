import asyncio
import json
from typing import Callable, Dict

import redis.asyncio as redis
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RedisEventBus:
    """Redis pub/sub event bus using shared Redis client."""
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize with existing Redis client from core.
        
        Args:
            redis_client: Shared Redis client instance from core.redis
        """
        self.redis_client = redis_client
        self.pubsub: redis.client.PubSub = None
        self.handlers: Dict[str, list] = {}
        self.listener_task: asyncio.Task = None

    async def connect(self):
        """Initialize pubsub connection."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not provided")
            self.pubsub = self.redis_client.pubsub()
            logger.info("Redis event bus pubsub initialized")
        except Exception as e:
            logger.exception(f"Failed to initialize Redis pubsub: {e}")
            raise

    async def disconnect(self):
        """Close pubsub connection (client managed by core)."""
        try:
            if self.listener_task:
                self.listener_task.cancel()
                try:
                    await self.listener_task
                except asyncio.CancelledError:
                    pass

            if self.pubsub:
                await self.pubsub.close()

            logger.info("Redis event bus pubsub closed")
        except Exception as e:
            logger.exception(f"Error during Redis pubsub disconnect: {e}")

    async def publish(self, event_name: str, payload: dict):
        try:
            if not self.redis_client:
                logger.error(
                    f"Redis client not initialized, cannot publish event: {event_name}"
                )
                return

            message = json.dumps({"event": event_name, "data": payload})
            logger.debug(f"Publishing event '{event_name}' to Redis: {payload}")
            await self.redis_client.publish("events", message)
            logger.debug(f"Event '{event_name}' published to Redis channel 'events'")
        except Exception as e:
            logger.exception(f"Failed to publish event '{event_name}': {e}")

    async def subscribe(self, event_name: str, handler: Callable):
        try:
            if event_name not in self.handlers:
                self.handlers[event_name] = []
            self.handlers[event_name].append(handler)
            logger.debug(f"Subscribed handler to event '{event_name}'")
        except Exception as e:
            logger.exception(f"Failed to subscribe to event '{event_name}': {e}")

    async def start_listener(self):
        try:
            if not self.pubsub:
                logger.error("PubSub not initialized, cannot start listener")
                return

            await self.pubsub.subscribe("events")
            self.listener_task = asyncio.create_task(self._listen())
            logger.info("Event listener started")
        except Exception as e:
            logger.exception(f"Failed to start event listener: {e}")

    async def _listen(self):
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        event_name = data.get("event")
                        payload = data.get("data", {})

                        if event_name in self.handlers:
                            for handler in self.handlers[event_name]:
                                asyncio.create_task(handler(payload))
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode event message: {e}")
                    except Exception as e:
                        logger.exception(f"Error processing event {event_name}: {e}")
        except asyncio.CancelledError:
            logger.info("Event listener cancelled")
        except Exception as e:
            logger.exception(f"Fatal error in event listener: {e}")


event_bus: RedisEventBus = None
