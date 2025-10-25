import redis.asyncio as redis
from redis.exceptions import ResponseError
import json
from typing import AsyncGenerator, Dict, Any
import os

class EventBus:
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis = None

    async def connect(self):
        """Establishes connection to Redis."""
        self._redis = redis.from_url(self.redis_url, decode_responses=True)
        await self._redis.ping()
        print(f"Connected to Redis at {self.redis_url}")

    async def disconnect(self):
        """Closes the Redis connection."""
        if self._redis:
            await self._redis.close()
            print("Disconnected from Redis.")

    async def publish(self, stream_name: str, event_data: Dict[str, Any]):
        """Publishes an event to a Redis Stream."""
        if not self._redis:
            raise ConnectionError("EventBus not connected. Call connect() first.")
        
        message_id = await self._redis.xadd(stream_name, {"data": json.dumps(event_data)})
        # print(f"Published to stream '{stream_name}' with ID: {message_id}")
        return message_id

    async def subscribe(self, stream_name: str, consumer_group: str, consumer_name: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Subscribes to a Redis Stream using a consumer group.
        Yields parsed event data.
        """
        if not self._redis:
            raise ConnectionError("RedisEventBus not connected. Call connect() first.")

        try:
            await self._redis.xgroup_create(stream_name, consumer_group, id='0', mkstream=True)
            print(f"Consumer group '{consumer_group}' created for stream '{stream_name}'.")
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
            # print(f"Consumer group '{consumer_group}' already exists for stream '{stream_name}'.")

        while True:
            try:
                # Read new messages
                messages = await self._redis.xreadgroup(
                    consumer_group,
                    consumer_name,
                    {stream_name: '>'},
                    count=1,
                    block=1000 # Block for 1 second
                )
                
                if messages:
                    for stream, message_list in messages:
                        for message_id, message_data in message_list:
                            # Acknowledge the message
                            await self._redis.xack(stream_name, consumer_group, message_id)
                            # print(f"Acknowledged message {message_id} from stream {stream_name}")
                            
                            # Parse and yield the event
                            if "data" in message_data:
                                yield json.loads(message_data["data"])
                            else:
                                print(f"Warning: Message {message_id} in stream {stream_name} has no 'data' field.")

            except Exception as e:
                print(f"Error during Redis stream subscription: {e}")
                # Depending on error, might want to re-establish connection or retry after a delay
