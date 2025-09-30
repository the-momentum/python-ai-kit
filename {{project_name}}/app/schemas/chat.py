from uuid import UUID

from pydantic import BaseModel


class CreateChatSessionResponse(BaseModel):
    conversation_id: UUID
    session_id: UUID