from datetime import datetime, timedelta
from pathlib import Path
from tabulate import tabulate
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


def open_db():
    rep_dir = find_rep_dir()
    db_dir = rep_dir.joinpath("database.json")
    db = tinydb.TinyDB(db_dir)
    return db


@app.command()
def init():
    try:
        rep_dir = Path(".rep")
        rep_dir.mkdir()
        db_dir = rep_dir.joinpath("database.json")
        with tinydb.TinyDB(db_dir) as db:
            db.insert(
                {
                    "type": "meta",
                    "create_time": datetime.now().isoformat(),
                }
            )
    except FileExistsError:
        typer.echo("Database already exists!")
        raise typer.Abort()


@app.command()
def start(note: str = None):
    with open_db() as db:
        log = db.table("log")
        data = log.all()
        if data and not data[-1]["end"]:
            typer.echo("You've already started!")
            raise typer.Abort()
        else:
            log.insert(
                {
                    "start": datetime.now().isoformat(),
                    "end": None,
                    "billed": False,
                }
            )


@app.command()
def stop(note: str = None):
    with open_db() as db:
        log = db.table("log")
        data = log.all()
        if data and data[-1]["end"]:
            typer.echo("You've already stopped!")
            raise typer.Abort()
        else:
            id = data[-1].doc_id
            log.update(
                {
                    "end": datetime.now().isoformat(),
                },
                doc_ids=[id],
            )


@app.command()
def note(message: str):
    with open_db() as db:
        log = db.table("log")
        notes = db.table("notes")
        if not log:
            typer.echo("No records to note on!")
            raise typer.Abort()
        else:
            id = log.all()[-1].doc_id
            notes.insert(
                {
                    "record_id": id,
                    "time": datetime.now().isoformat(),
                    "message": message,
                }
            )


@app.command()
def dump():
    with open_db() as db:
        log = db.table("log")
        data = log.all()
        if data:
            headers = {
                "Start": "start",
                "End": "end",
                "Billed": "billed",
            }
            typer.echo(tabulate(data, headers=headers, tablefmt="psql"))
        else:
            typer.echo("Empty.")


@app.command("print")
def _print():
    pass


@app.command()
def invoice(rate: float):
    with open_db() as db:
        log = db.table("log")
        Log = tinydb.Query()
        data = log.search(Log.billed == False)
        time = timedelta()
        for doc in data:
            start = datetime.fromisoformat(doc["start"])
            end = datetime.fromisoformat(doc["end"])
            assert end >= start
            time += end - start
        hours = time.total_seconds() / 60.0 / 60.0
        bill = hours * rate
        typer.echo("Bill ${:.2f} for {:.2f}h".format(bill, hours))


@app.command()
def bill():
    with open_db() as db:
        # TODO: Confirmation dialog
        # TODO: Print billed hours
        log = db.table("log")
        log.update({"billed": True})


if __name__ == "__main__":
    app()