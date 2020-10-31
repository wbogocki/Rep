from datetime import datetime
from pydantic import BaseModel


class LogEntry(BaseModel):
    start: datetime
    end: datetime
    billed: bool


class Note(BaseModel):
    log_entry_id: int
    message: str
    time: datetime