"""
WebSocket Manager - Real-time Communication

Implements WebSocket support as outlined in PROJECT_OVERVIEW.md:
- Real-time chat with Ruby and other assistants
- Connection management
- Message broadcasting
"""

from typing import List
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

from crystal.utils.logging import CrystalLogger

class WebSocketManager:
    """
    Manages WebSocket connections for real-time communication.
    
    Supports the real-time chat functionality outlined in PROJECT_OVERVIEW.md
    for immediate interaction with assistants.
    """
    
    def __init__(self):
        self.logger = CrystalLogger("websocket_manager")
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and manage new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        self.logger.system_event(
            "websocket_connected",
            active_connections=len(self.active_connections)
        )
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        self.logger.system_event(
            "websocket_disconnected", 
            active_connections=len(self.active_connections)
        )
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            self.logger.error("websocket_send_failed", error=str(e))
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        if self.active_connections:
            message_text = json.dumps(message)
            for connection in self.active_connections[:]:  # Copy list to avoid issues during iteration
                try:
                    await connection.send_text(message_text)
                except Exception as e:
                    self.logger.error("websocket_broadcast_failed", error=str(e))
                    # Remove failed connection
                    self.disconnect(connection)
