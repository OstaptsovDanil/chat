from collections import defaultdict
from typing import Callable

from starlette.websockets import WebSocket


class WebSocketConnectionManager:
    def __init__(self):
        self.chat_websockets: dict[int, list[WebSocket]] = defaultdict(list)
        self.user_websockets: dict[int, list[WebSocket]] = defaultdict(list)
        self.user_chats: dict[int, list[int]] = defaultdict(list)
        self.handlers: dict[str, Callable] = {}

    def handler(self, message_type: str):
        def decorator(func):
            self.handlers[message_type] = func
            return func

        return decorator

    async def connect(self, websocket: WebSocket, user_id: int, chat_ids: list[int]):
        await websocket.accept()
        self.user_websockets[user_id].append(websocket)
        for chat_id in chat_ids:
            self.chat_websockets[chat_id].append(websocket)
        self.user_chats = chat_ids

    def disconnect(self, user_id: int, websocket: WebSocket):
        self.chat_websockets[user_id].remove(websocket)
        for chat_id in self.user_chats[user_id]:
            if websocket in self.chat_websockets[chat_id]:
                self.chat_websockets[chat_id].remove(websocket)

    async def broadcast_to_chat(self, chat_id: int, message: dict):
        for connection in self.chat_websockets[chat_id]:
            await connection.send_json(message)

    async def broadcast_to_user(self, user_id: int, message: dict):
        for connection in self.user_websockets[user_id]:
            await connection.send_json(message)

    async def send_error(self, message: str, websocket: WebSocket):
        await websocket.send_json({'status': 'error', 'message': message})


websocket_manager = WebSocketConnectionManager()
