from datetime import datetime
from pathlib import Path
import tinydb
import typer

app = typer.Typer()


def find_rep_dir(_current=Path(".").resolve()):
    path = _current
    test = path.joinpath(".rep")
    if test.exists() and test.is_dir():
        return test
    elif path == path.parent:
        typer.echo("Database not found!")
        raise typer.Abort()
    else:
        return find_rep_dir(path.parent)


@app.command()
def init():
    try:
        rep_dir = Path(".rep")
        rep_dir.mkdir()
        db_dir = rep_dir.joinpath("database.json")
        db = tinydb.TinyDB(db_dir)
        db.insert({"type": "metadata", "init_time": datetime.now().isoformat()})
    except FileExistsError:
        typer.echo("Database already exists!")
        raise typer.Abort()


@app.command()
def start(note: str = None):
    dir = find_rep_dir()
    print(f"stop {note}")


@app.command()
def stop(note: str = None):
    dir = find_rep_dir()
    print(f"stop {note}")


@app.command()
def note(note: str):
    dir = find_rep_dir()
    print(f"note {note}")


if __name__ == "__main__":
    app()