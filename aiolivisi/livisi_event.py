from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional


@dataclass(init=False)
class LivisiEvent(BaseModel):
    namespace: str
    properties: Optional[dict]
    source: str
    onState: Optional[bool]
    vrccData: Optional[float]
    isReachable: Optional[bool]
    sequenceNumber: Optional[str]
    type: Optional[str]
    timestamp: Optional[str]
