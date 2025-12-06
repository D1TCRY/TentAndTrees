import pathlib


def _char_to_target(char: str) -> int:
    """Converte un carattere del file livello in un numero target."""
    if char == ".":
        return 0
    if char.isdigit():
        return int(char)
    raise ValueError(f"Invalid target char: {char}")


class Level:
    def __init__(
        self,
        path: pathlib.Path | str,
        columns: int,
        lines: int,
        columns_targets: list[int],
        rows_targets: list[int],
        trees: set[tuple[int, int]] | None = None,
        correct_tents: set[tuple[int, int]] | None = None
    ) -> None:
        """Contenitore "pulito" dei dati di un livello."""
        self.path = path
        self.columns = columns
        self.lines = lines
        self.columns_targets = columns_targets
        self.rows_targets = rows_targets
        self.trees = trees or set()
        self.correct_tents = correct_tents or set()

    def __str__(self) -> str:
        return f"< {self.__class__.__name__} | {self.path.name}, {self.difficulty}, {self.columns}x{self.lines} >"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if other is self:
            return True
        if not isinstance(other, Level):
            return NotImplemented
        return (
                self.path.resolve() == other.path.resolve()
                and self.columns == other.columns
                and self.lines == other.lines
                and self.columns_targets == other.columns_targets
                and self.rows_targets == other.rows_targets
                and self.trees == other.trees
        )

    def __hash__(self) -> int:
        return hash((
            self.path.resolve(),
            self.columns,
            self.lines,
            tuple(self.columns_targets),
            tuple(self.rows_targets),
            frozenset(self.trees),
        ))

    # ======== PROPERTIES ========
    @property
    def path(self) -> pathlib.Path:
        return self.__path
    @path.setter
    def path(self, value: pathlib.Path | str) -> None:
        if not isinstance(value, (pathlib.Path, str)):
            raise TypeError("path must be pathlib.Path or str")
        self.__path = pathlib.Path(value) if isinstance(value, str) else value

    @property
    def columns(self) -> int:
        return self.__columns
    @columns.setter
    def columns(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("columns must be int")
        if value <= 0:
            raise ValueError("columns must be > 0")
        self.__columns = value

    @property
    def lines(self) -> int:
        return self.__lines
    @lines.setter
    def lines(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("lines must be int")
        if value <= 0:
            raise ValueError("lines must be > 0")
        self.__lines = value

    @property
    def columns_targets(self) -> list[int]:
        return self.__columns_targets
    @columns_targets.setter
    def columns_targets(self, value: list[int]) -> None:
        if not isinstance(value, list):
            raise TypeError("columns_targets must be list[int]")
        if any((not isinstance(x, int) or x < 0) for x in value):
            raise ValueError("columns_targets must contain ints >= 0")
        self.__columns_targets = value

    @property
    def rows_targets(self) -> list[int]:
        return self.__rows_targets
    @rows_targets.setter
    def rows_targets(self, value: list[int]) -> None:
        if not isinstance(value, list):
            raise TypeError("rows_targets must be list[int]")
        if any((not isinstance(x, int) or x < 0) for x in value):
            raise ValueError("rows_targets must contain ints >= 0")
        self.__rows_targets = value

    @property
    def trees(self) -> set[tuple[int, int]]:
        return self.__trees
    @trees.setter
    def trees(self, value: set[tuple[int, int]]) -> None:
        if not isinstance(value, set):
            raise TypeError("trees must be set[tuple[int,int]]")
        for t in value:
            if not isinstance(t, tuple) or len(t) != 2:
                raise TypeError("trees must contain tuples (x,y)")
            x, y = t
            if not isinstance(x, int) or not isinstance(y, int):
                raise TypeError("tree coordinates must be int")
        self.__trees = value

    @property
    def correct_tents(self) -> set[tuple[int, int]]:
        return self.__correct_tents
    @correct_tents.setter
    def correct_tents(self, value: set[tuple[int, int]]) -> None:
        if not isinstance(value, set):
            raise TypeError("correct_tents must be set[tuple[int,int]]")
        for t in value:
            if not isinstance(t, tuple) or len(t) != 2:
                raise TypeError("correct_tents must contain tuples (x,y)")
            x, y = t
            if not isinstance(x, int) or not isinstance(y, int):
                raise TypeError("correct_tent coordinates must be int")
        self.__correct_tents = value

    @property
    def difficulty(self) -> str:
        """Prova a ricavare la difficoltà dal nome file."""
        # tents-2025-11-27-8x8-easy.txt -> "easy"
        stem = self.path.stem
        if "-" not in stem:
            return "unknown"
        return stem.split("-")[-1].lower()

    # ======== PARSING ========
    @classmethod
    def from_file(cls, path: pathlib.Path | str) -> "Level":
        """
            Carica e interpreta un file di livello (.txt) e lo trasforma in un oggetto Level.

            Formato atteso:
            - prima riga: un carattere char + target colonne (cifre o '.')
            - righe successive: target riga + griglia lunga quanto le colonne
              * '.' = vuoto
              * 'T' = albero
              * '^' = tenda soluzione
        """
        p = pathlib.Path(path)
        raw: list[str] = [line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(raw) < 2:
            raise ValueError(f"{p.name}: file must contain at least 2 lines")

        header = raw[0]
        if len(header) < 2:
            raise ValueError(f"{p.name}: invalid header line: {header}")

        col_targets = [_char_to_target(ch) for ch in header[1:]]
        cols = len(col_targets)

        grid_lines = raw[1:]
        rows = len(grid_lines)

        row_targets: list[int] = []
        trees: set[tuple[int, int]] = set()
        tents: set[tuple[int, int]] = set()

        for y, line in enumerate(grid_lines):
            if len(line) != 1 + cols:
                raise ValueError(f"{p.name}: row {y} length {len(line)} != {1 + cols} ({line})")

            row_targets.append(_char_to_target(line[0]))

            for x, char in enumerate(line[1:]):
                if char == ".":
                    continue
                if char.upper() == "T":
                    trees.add((x, y))
                elif char == "^":
                    tents.add((x, y))
                else:
                    raise ValueError(f"{p.name}: invalid cell char {char!r} at {(x, y)}")

        lvl = cls(
            path=p,
            columns=cols,
            lines=rows,
            columns_targets=col_targets,
            rows_targets=row_targets,
            trees=trees,
            correct_tents=tents
        )

        # -> coerenza targets vs dimensioni
        if len(lvl.columns_targets) != lvl.columns:
            raise ValueError(f"{p.name}: columns_targets length mismatch")
        if len(lvl.rows_targets) != lvl.lines:
            raise ValueError(f"{p.name}: rows_targets length mismatch")

        return lvl