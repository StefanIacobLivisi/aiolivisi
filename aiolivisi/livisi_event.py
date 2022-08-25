from pydantic import BaseModel
from typing import Optional

class LivisiEvent(BaseModel):
    namespace: str
    properties: Optional[dict]
    source: str
    onState: Optional[bool]
    isReachable: Optional[bool]