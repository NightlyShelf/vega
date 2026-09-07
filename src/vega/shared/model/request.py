from uuid import UUID

from pydantic import BaseModel


class Request(BaseModel):
    room: str
    device: str
    request_id: UUID
    content: str
