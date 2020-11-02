from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Config(BaseModel):
    bill_rate: int


class Note(BaseModel):
    time: datetime
    message: str


class Log(BaseModel):
    start_tm: datetime
    end_tm: Optional[datetime]
    notes: List[Note]
    is_billed: bool
