import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.api.websockets.manager import ws_manager

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Main WebSocket endpoint for the frontend dashboard to connect to.
    Listens for heartbeats to keep the connection alive.
    """
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            # Wait for messages from the client (e.g. ping/heartbeat)
            data = await websocket.receive_text()
            if data.lower() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        ws_manager.disconnect(websocket, client_id)
