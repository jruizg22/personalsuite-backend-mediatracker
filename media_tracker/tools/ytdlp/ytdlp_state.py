from dataclasses import dataclass
from threading import Lock


@dataclass
class YTDLPUpdateState:
    updating: bool = False
    last_error: str | None = None


update_lock = Lock()
update_state = YTDLPUpdateState()