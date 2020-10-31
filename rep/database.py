from .models import LogEntry, Note
from tinydb import TinyDB

# Log Entries


def create_log_entry(db: TinyDB, entry: LogEntry):
    pass


def read_log_entry(db: TinyDB, id: int):
    pass


def write_log_entry(db: TinyDB, id: int, entry: LogEntry):
    pass


# Notes


def create_note(db: TinyDB, note: Note):
    pass


def read_note(db: TinyDB, id: int):
    pass


def write_note(db: TinyDB, id: int, note: Note):
    pass