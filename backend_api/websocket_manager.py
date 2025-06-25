from fastapi import WebSocket 
from typing import List 

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)
    
    def disconnect(self, ws: WebSocket):
        self.active_connections.remove(ws)

    async def broadcast(self, message: dict):
        for conn in self.active_connections:
            await conn.send_json(message)

manager = ConnectionManager() 
