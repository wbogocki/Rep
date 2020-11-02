from database import DateTimeSerializer
from datetime import datetime, timedelta
from models import Config, Note, Log
from pathlib import Path
from tabulate import tabulate
from tinydb import TinyDB, Query
from tinydb_serialization import SerializationMiddleware
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
    storage = SerializationMiddleware()
    storage.register_serializer(DateTimeSerializer(), "datetime")
    path = find_rep_dir() / "database.json"
    return TinyDB(path, storage=storage)


@app.command()
def init():
    try:
        # Prompt for config
        bill_rate = typer.prompt("What's your bill rate?")
        config = Config(bill_rate=bill_rate)

        # Make Rep directory
        dir = Path(".rep")
        dir.mkdir()

        # Create and initialize the database
        with open_db() as db:
            db.table("config").insert(config.dict())

    except FileExistsError:
        typer.echo("Database already exists!")
        raise typer.Abort()


@app.command()
def start(note: str = None):
    with open_db() as db:
        logs = db.table("logs")

        # Check if we aren't already started
        if logs:
            last = Log.parse_obj(logs.all()[-1])
            if not last.end_tm:
                typer.echo("Already started!")
                raise typer.Abort()
        else:
            log = Log(start_tm=datetime.now(), notes=[], is_billed=False)
            logs.insert(log.dict())


@app.command()
def stop(note: str = None):
    with open_db() as db:
        logs = db.table("logs")

        # Check if we are started
        if not logs:
            typer.echo("Never started!")
            raise typer.Abort()
        else:
            doc = logs.all()[-1]
            log = Log.parse_obj(doc)

            # Check if aren't already stopped
            if log.end_tm:
                typer.echo("Already stopped!")
                raise typer.Abort()
            else:
                log.end_tm = datetime.now()
                logs.update(log.dict(), doc_ids=[doc.doc_id])


@app.command()
def note(message: str):
    with open_db() as db:
        logs = db.table("logs")
        if not logs:
            typer.echo("No records to note on!")
            raise typer.Abort()
        else:
            doc = logs.all()[-1]
            log = Log.parse_obj(doc)
            log.notes.append(Note(time=datetime.now(), message=message))
            logs.update(log.dict(), doc_ids=[doc.doc_id])


@app.command()
def dump():
    with open_db() as db:
        logs = db.table("logs").all()
        if logs:

            def table_row(doc):
                time_fmt = "%a, %b %-d %Y, %-I:%M %p"
                log = Log.parse_obj(doc)
                return {
                    "ID": doc.doc_id,
                    "Start": log.start_tm.strftime(time_fmt),
                    "End": log.end_tm.strftime(time_fmt),
                    "Notes": len(log.notes),
                    "Billed": "Yes" if log.is_billed else "No",
                }

            table = tabulate(map(table_row, logs), headers="keys", tablefmt="psql")
            typer.echo(table)
        else:
            typer.echo("Empty.")


@app.command("print")
def _print():
    # with open_db() as db:
    #     log = db.table("log")
    #     notes = db.table("notes")
    #     for entry in log:
    #         id = entry.doc_id
    #         start = entry["start"]
    #         end = entry["end"]
    #         billed = "*" if entry["billed"] else " "
    #         typer.echo(f"({id}) {start} to {end} [{billed}]")

    #         Note = tinydb.Query()
    #         for note in notes.search(Note.record_id == id):
    #             time = note["time"]
    #             message = note["message"]
    #             typer.echo(f"- {time} {message}")
    pass


@app.command()
def invoice(rate: float):
    # with open_db() as db:
    #     log = db.table("log")
    #     Log = tinydb.Query()
    #     data = log.search(Log.billed == False)
    #     time = timedelta()
    #     for doc in data:
    #         start = datetime.fromisoformat(doc["start"])
    #         end = datetime.fromisoformat(doc["end"])
    #         assert end >= start
    #         time += end - start
    #     hours = time.total_seconds() / 60.0 / 60.0
    #     bill = hours * rate
    #     typer.echo("Bill ${:.2f} for {:.2f}h".format(bill, hours))
    pass


@app.command()
def bill():
    # with open_db() as db:
    #     # TODO: Confirmation dialog
    #     # TODO: Print billed hours
    #     log = db.table("log")
    #     log.update(
    #         {
    #             "billed": True,
    #             "billed_on": datetime.now().isoformat(),
    #         }
    #     )
    pass


if __name__ == "__main__":
    app()