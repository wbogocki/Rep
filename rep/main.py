from .database import open_db
from .models import Config, Note, Log
from datetime import datetime, timedelta
from pathlib import Path
from tabulate import tabulate
from tinydb import where
import typer

app = typer.Typer()


@app.command(help="Initialize Rep in the current directory.")
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
        typer.echo("Database already exists.")
        raise typer.Abort()


@app.command(help="Open a new log and start measuring time.")
def start(note: str = None):
    with open_db() as db:
        logs = db.table("logs")

        # Check if we aren't already started
        if logs:
            last = Log.parse_obj(logs.all()[-1])
            if not last.end_tm:
                typer.echo("Already started.")
                raise typer.Abort()

        log = Log(start_tm=datetime.now(), notes=[], is_billed=False)
        logs.insert(log.dict())

    typer.echo("Started.")


@app.command(help="Close the current log and stop measuring time.")
def stop(note: str = None):
    with open_db() as db:
        logs = db.table("logs")

        # Check if we nver started
        if not logs:
            typer.echo("Never started.")
            raise typer.Abort()

        doc = logs.all()[-1]
        log = Log.parse_obj(doc)

        # Check if aren't already stopped
        if log.end_tm:
            typer.echo("Already stopped.")
            raise typer.Abort()

        log.end_tm = datetime.now()
        logs.update(log.dict(), doc_ids=[doc.doc_id])

    typer.echo("Stopped.")


@app.command(help="Add a note to the last log.")
def note(message: str):
    with open_db() as db:
        logs = db.table("logs")
        if not logs:
            typer.echo("No records to note on.")
            raise typer.Abort()
        else:
            doc = logs.all()[-1]
            log = Log.parse_obj(doc)
            log.notes.append(Note(time=datetime.now(), message=message))
            logs.update(log.dict(), doc_ids=[doc.doc_id])

    typer.echo("Note added.")


@app.command(help="Print logs in a table.")
def table():
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


@app.command("print", help="Print logs and notes.")
def _print():
    with open_db() as db:
        logs = db.table("logs")
        if logs:
            for i, doc in enumerate(logs):
                time_fmt = "%a, %b %-d %Y, %-I:%M %p"
                log = Log.parse_obj(doc)

                typer.echo(f"({doc.doc_id})")
                typer.echo(f"Start:  {log.start_tm.strftime(time_fmt)}")
                typer.echo(f"End:    {log.end_tm.strftime(time_fmt)}")
                typer.echo(f"Notes:  {len(log.notes)}")
                typer.echo(f"Billed: {'Yes' if log.is_billed else 'No'}")
                typer.echo()

                for note in log.notes:
                    typer.echo(f"> {note.time.strftime(time_fmt)}")
                    typer.echo(f"{note.message}")
                    typer.echo()

                if i + 1 != len(logs):
                    typer.echo("------")
                    typer.echo()
        else:
            typer.echo("Empty.")


@app.command(help="Calculate invoice for unbilled logs.")
def invoice():
    with open_db() as db:
        logs = db.table("logs").search(where("is_billed") == False)

        time_acc = timedelta()
        for doc in logs:
            log = Log.parse_obj(doc)

            # Sanity check: must not be running
            if not log.end_tm:
                typer.echo("Warning: currently counting time!")
                continue

            # Sanity check: end must happen after starting
            assert (
                log.end_tm >= log.start_tm
            ), f"Log {doc.doc_id}: end time is ahead of start time."

            time_acc += log.end_tm - log.start_tm

        config = Config.parse_obj(db.table("config").get(doc_id=1))

        bill_rate = config.bill_rate
        hours = time_acc.total_seconds() / 60.0 / 60.0
        bill = bill_rate * hours

        typer.echo(f"Bill ${bill:.2f} for {hours:.2f}h at ${bill_rate}/h.")


@app.command(help="Mark logs as billed.")
def bill():
    with open_db() as db:
        answer = typer.confirm("Are you sure you want to mark all logs as billed?")
        if not answer:
            raise typer.Abort()
        logs = db.table("logs")
        docs = logs.update({"is_billed": True}, where("is_billed") == False)

    typer.echo(f"Billed {len(docs)} logs.")


if __name__ == "__main__":
    app()