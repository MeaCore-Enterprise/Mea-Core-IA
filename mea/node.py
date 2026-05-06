import asyncio
import json
import uuid
import redis.asyncio as redis
import traceback

class SwarmNode:
    """
    Manages connections to the Redis-based Swarm network.
    Allows passing messages between distributed PCs.
    """
    def __init__(self, node_id=None, redis_url="redis://localhost:6379"):
        self.node_id = node_id or str(uuid.uuid4())[:8]
        self.redis_url = redis_url
        self.redis = None
        self.pubsub = None
        self.is_running = False
        self.handlers = {}
        
    async def connect(self):
        """Connects to the redis message broker."""
        self.redis = redis.Redis.from_url(self.redis_url)
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe("swarm_channel")
        self.is_running = True
        print(f"[Node {self.node_id}] Connected to Swarm at {self.redis_url}")
        asyncio.create_task(self._listen())
        
    def on(self, event_type, handler):
        """Register an async handler for a specific event type."""
        self.handlers[event_type] = handler

    async def broadcast(self, event_type, payload):
        """Broadcast an event to all nodes in the swarm."""
        if not self.redis:
            raise Exception("Node not connected")
        message = {
            "source_id": self.node_id,
            "type": event_type,
            "payload": payload
        }
        await self.redis.publish("swarm_channel", json.dumps(message))

    async def _listen(self):
        """Background task listening for swarm messages."""
        try:
            async for message in self.pubsub.listen():
                if not self.is_running:
                    break
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    # Ignore our own messages
                    if data["source_id"] != self.node_id:
                        event_type = data.get("type")
                        if event_type in self.handlers:
                            # Run the handler concurrently
                            asyncio.create_task(self.handlers[event_type](data["payload"]))
        except Exception as e:
            print(f"[Node {self.node_id}] Listen error: {e}")
            traceback.print_exc()

    async def disconnect(self):
        """Cleanly disconnects the node."""
        self.is_running = False
        if self.pubsub:
            await self.pubsub.unsubscribe("swarm_channel")
        if self.redis:
            await self.redis.aclose()
        print(f"[Node {self.node_id}] Disconnected.")
