import pathlib
import json

from .level import Level


DEFAULT = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "levels"


def show_levels(path: pathlib.Path | str = DEFAULT) -> list[Level]:
    """Scansiona la cartella dei livelli e carica tutti i file .txt come oggetti Level."""
    folder = pathlib.Path(path) if isinstance(path, str) else path
    if not folder.exists():
        return []

    levels: list[Level] = []
    for file in sorted(folder.glob("*.txt")):
        try:
            levels.append(Level.from_file(file))
        except Exception as e:
            print(f"[skip] {file.name}: {e}")

    return levels


def read_settings():
    """Legge il file data/settings.json e ritorna un dizionario con le impostazioni."""
    path = pathlib.Path(__file__).resolve().parents[2] / "data" / "settings.json"
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"<file_management.py | File not found {path}>")
        return {}
    except json.JSONDecodeError as e:
        print(f"<file_management.py | Error parsing JSON: {e}>")
        return {}