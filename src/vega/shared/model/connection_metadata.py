from pydantic import BaseModel
from enum import Enum

class ConnectionMetadata(BaseModel):
    device: str
    type: ConnectionType

class ConnectionType(Enum):
    INPUT = 1
    OUTPUT = 2