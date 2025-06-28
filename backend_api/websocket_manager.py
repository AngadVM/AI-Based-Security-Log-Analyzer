from fastapi import WebSocket
from typing import List


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.copy():  # Copy to avoid iteration issues
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f" WebSocket error: {e}")
                self.disconnect(connection)


manager = ConnectionManager()
