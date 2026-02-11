import asyncio
import json
from typing import Callable, Dict

import redis.asyncio as redis


class RedisEventBus:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client: redis.Redis = None
        self.pubsub: redis.client.PubSub = None
        self.handlers: Dict[str, list] = {}
        self.listener_task: asyncio.Task = None

    async def connect(self):
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()

    async def disconnect(self):
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass

        if self.pubsub:
            await self.pubsub.close()

        if self.redis_client:
            await self.redis_client.close()

    async def publish(self, event_name: str, payload: dict):
        if not self.redis_client:
            print(
                f"[ERROR] Redis client not initialized, cannot publish event: {event_name}"
            )
            return

        message = json.dumps({"event": event_name, "data": payload})
        print(f"[DEBUG] Publishing event '{event_name}' to Redis: {payload}")
        await self.redis_client.publish("events", message)
        print(f"[DEBUG] Event '{event_name}' published to Redis channel 'events'")

    async def subscribe(self, event_name: str, handler: Callable):
        if event_name not in self.handlers:
            self.handlers[event_name] = []
        self.handlers[event_name].append(handler)

    async def start_listener(self):
        if not self.pubsub:
            return

        await self.pubsub.subscribe("events")
        self.listener_task = asyncio.create_task(self._listen())

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
                    except Exception as e:
                        print(f"Error processing event {event_name}: {e}")
                        import traceback

                        traceback.print_exc()
        except asyncio.CancelledError:
            pass


event_bus: RedisEventBus = None
