from datetime import datetime
from pathlib import Path
from tinydb import TinyDB
from tinydb_serialization import Serializer, SerializationMiddleware
import typer


class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime

    def encode(self, obj: datetime):
        return obj.isoformat()

    def decode(self, s: str) -> datetime:
        return datetime.fromisoformat(s)


def _find_rep_dir(_current=Path(".").resolve()):
    path = _current
    test = path.joinpath(".rep")
    if test.exists() and test.is_dir():
        return test
    elif path == path.parent:
        typer.echo("Database not found.")
        raise typer.Abort()
    else:
        return _find_rep_dir(path.parent)


def open_db():
    storage = SerializationMiddleware()
    storage.register_serializer(DateTimeSerializer(), "datetime")
    path = _find_rep_dir() / "database.json"
    return TinyDB(path, storage=storage)
