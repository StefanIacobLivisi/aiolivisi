from pydantic import BaseModel

class EventData(BaseModel):
    namespace: str
    properties: dict
    deviceConfigurationState: str
    deviceInclusionState: str
    firmwareVersion: str
    onState: bool
    isReachable: bool
    updateState: str
    sequenceNumber: int
    source: str
    timestamp: str
    type: str