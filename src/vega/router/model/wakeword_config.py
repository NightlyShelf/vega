from pydantic import BaseModel


class AgentModel(BaseModel):
    name: str
    endpoint: str
    wakewords: list[str]
    auth_header: str


class WakeWordConfig(BaseModel):
    agents: list[AgentModel]
