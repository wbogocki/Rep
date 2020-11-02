from datetime import datetime
from tinydb import TinyDB
from tinydb_serialization import Serializer


class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime

    def encode(self, obj: datetime):
        return obj.isoformat()

    def decode(self, s: str) -> datetime:
        return datetime.fromisoformat(s)
