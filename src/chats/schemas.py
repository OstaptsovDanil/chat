from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageReadEventSchema(BaseModel):
    id: int
    chat_id: int


class MessageReadNotificationSchema(BaseModel):
    id: int
    user_id: int
    chat_id: int


class MessageCreateSchema(BaseModel):
    user_id: int
    chat_id: int
    text: str


class NewMessageNotificationSchema(BaseModel):
    id: int
    user_id: int
    chat_id: int
    text: str
    dt_created: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageSchema(BaseModel):
    id: int
    user_id: int
    text: str
    dt_created: datetime

    model_config = ConfigDict(from_attributes=True)


class ReadCursorSchema(BaseModel):
    user_id: int
    message_id: int

    model_config = ConfigDict(from_attributes=True)


class MessageListFromChatSchema(BaseModel):
    messages: list[MessageSchema]
    read_cursors: list[ReadCursorSchema]
