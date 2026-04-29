from pydantic import BaseModel


class YTDLPStatus(BaseModel):
    installed: str
    latest: str
    update_available: bool
    updating: bool

class YTDLPUpdateResult(BaseModel):
    old_version: str
    new_version: str
    updated: bool