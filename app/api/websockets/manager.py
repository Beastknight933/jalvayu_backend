import json
from typing import Dict, List
from fastapi import WebSocket
from loguru import logger

class ConnectionManager:
    """
    Manages active WebSocket connections for real-time dashboard updates.
    Supports targeted messaging by client ID and global broadcasting.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        logger.info(f"WebSocket client {client_id} connected. Active clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        logger.info(f"WebSocket client {client_id} disconnected.")

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send WS message to {client_id}: {e}")

    async def broadcast(self, message: dict):
        """
        Broadcasts a message to all connected clients (e.g. system-wide alerts or twin state changes).
        """
        payload = json.dumps(message)
        for client_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(payload)
                except Exception as e:
                    logger.error(f"Failed to broadcast to {client_id}: {e}")

ws_manager = ConnectionManager()
