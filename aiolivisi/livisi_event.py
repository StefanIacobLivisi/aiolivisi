from dataclasses import dataclass
try:
    from pydantic import BaseModel
except ImportError:
    from pydantic.v1 import BaseModel
from typing import Optional


@dataclass(init=False)
class LivisiEvent(BaseModel):
    namespace: str
    properties: Optional[dict]
    source: str
    onState: Optional[bool]
    vrccData: Optional[float]
    luminance: Optional[int]
    isReachable: Optional[bool]
    sequenceNumber: Optional[str]
    type: Optional[str]
    timestamp: Optional[str]
    isOpen: Optional[bool]
    keyIndex: Optional[int]
    isLongKeyPress: Optional[bool]
