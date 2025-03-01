from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from src.chats.schemas import NewMessageNotificationSchema, MessageCreateSchema, MessageReadEventSchema, \
    MessageReadNotificationSchema
from src.chats.selectors import message_create, message_read, message_filter_by_id, is_user_in_chat
from src.websockets.connection_manager import websocket_manager


@websocket_manager.handler('new_message')
async def new_message_handler(
    event: dict,
    user_id: int,
    session: AsyncSession,
    websocket: WebSocket,
    **kwargs,
):
    message_schema = MessageCreateSchema(**event)
    user_has_chat = await is_user_in_chat(session, user_id, message_schema.chat_id)
    if not user_has_chat:
        websocket_manager.send_error('Chat not found', websocket)
        return

    message = await message_create(session, user_id, message_schema.chat_id, message_schema.text)

    message_data = NewMessageNotificationSchema.from_orm(message).dict()
    message_data['event_type'] = 'new_message'
    await websocket_manager.broadcast_to_chat(message_schema.chat_id, message_data)


@websocket_manager.handler('read_message')
async def read_message_handler(
    event: dict,
    user_id: int,
    session: AsyncSession,
    websocket: WebSocket,
    **kwargs,
):
    message_read_schema = MessageReadEventSchema(**event)
    message = await message_filter_by_id(session, message_read_schema.id)

    if not message or message.chat_id != message_read_schema.chat_id:
        websocket_manager.send_error('Message does not exists', websocket)
        return

    await message_read(session, user_id, message_read_schema.chat_id, message)
    notification_data = MessageReadNotificationSchema(
        id=message.id,
        user_id=user_id,
        chat_id=message_read_schema.chat_id,
    ).dict()
    notification_data['event_type'] = 'read_message'
    await websocket_manager.broadcast_to_user(message.user_id, notification_data)

