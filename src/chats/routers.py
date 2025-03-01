from fastapi import APIRouter, HTTPException
from jwt import PyJWTError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.exc import FlushError
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.chats.schemas import MessageListFromChatSchema
from src.chats.selectors import messages_from_chat, is_user_in_chat, read_cursors_from_chat, chat_filter_by_user
from src.database.base import SessionDep
from src.dependencies import CurrentUserDep
from src.users.services.selectors import user_filter_by_token
from src.websockets.handlers import websocket_manager

chat_router = APIRouter(tags=['Chat'], prefix='/chats')


@chat_router.get('/{chat_id}/messages', response_model=MessageListFromChatSchema)
async def get_messages_from_chat(
    user: CurrentUserDep,
    chat_id: int,
    session: SessionDep,
    limit: int | None = None,
    offset: int | None = None,
):
    user_has_chat = await is_user_in_chat(session, user.id, chat_id)
    if not user_has_chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    messages = await messages_from_chat(session, chat_id, limit, offset)
    read_cursors = await read_cursors_from_chat(session, chat_id)

    return MessageListFromChatSchema(messages=messages, read_cursors=read_cursors)


@chat_router.websocket('/ws')
async def websocket_chat(websocket: WebSocket, token: str, session: SessionDep):
    try:
        user = await user_filter_by_token(session, token)
    except (ValueError, PyJWTError, NoResultFound) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))

    user_id = user.id
    user_chat_ids = await chat_filter_by_user(session, user_id)
    await websocket_manager.connect(websocket, user_id, user_chat_ids)

    try:
        while True:
            event = await websocket.receive_json()
            event_type = event.get('type')
            if not event_type:
                await websocket_manager.send_error('Field "type" is required', websocket)
                continue

            handler = websocket_manager.handlers.get(event_type)
            if not handler:
                await websocket_manager.send_error(f'Unknown event type {websocket_manager.handlers.keys()}', websocket)
                continue

            await handler(
                websocket=websocket,
                session=session,
                event=event,
                user_id=user_id,
            )

    except FlushError:
        await websocket.close()
        websocket_manager.disconnect(user_id, websocket)

    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id, websocket)

