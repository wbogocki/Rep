from pathlib import Path
import tinydb
import typer

app = typer.Typer()


def find_rep_dir(_current=Path(".").resolve()):
    path = _current
    test = path.joinpath(".rep")
    if test.exists() and test.is_dir():
        return test
    else:
        if path == path.parent:
            return None
        else:
            return find_rep_dir(path.parent)


@app.command()
def init():
    dir = find_rep_dir()
    print(f"{dir}")


@app.command()
def start(note: str = None):
    print(f"stop {note}")


@app.command()
def stop(note: str = None):
    print(f"stop {note}")


@app.command()
def note(note: str):
    print(f"note {note}")


if __name__ == "__main__":
    app()