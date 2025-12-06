from __future__ import annotations

from .gui_component import GUIComponent
from .cell import Cell


class Board(GUIComponent):
    def __init__(
        self,
        master,
        x: int,
        y: int,
        width: int,
        height: int,
        padding: int
    ) -> None:
        self.master = master
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = padding

        self._cells: list[Cell] | None = None

    @property
    def cells(self) -> list[Cell]:
        """
            Costruisce la griglia di Cell solo la prima volta, poi la riusa.

            - aggiunge 1 riga in alto per i target di colonna
            - aggiunge 1 colonna a sinistra per i target di riga
            - l'angolo (0, 0) resta vuoto

            Le celle interne hanno un comando di click che chiama master.play(...)
            con action None, così si usa il comportamento "toggle" gestito dal Game.
        """
        if self._cells is not None:
            return self._cells

        cols = self.master.cols() + 1
        rows = self.master.rows() + 1

        cols_targets = self.master.columns_targets
        rows_targets = self.master.rows_targets

        cell_width = (self.width - (self.padding * cols)) / cols
        cell_height = (self.height - (self.padding * rows)) / rows

        def cell_xy(j: int, i: int) -> tuple[float, float]:
            x = self.x + (j * cell_width) + (self.padding * j)
            y = self.y + (i * cell_height) + (self.padding * i)
            return x, y

        cells: list[Cell] = []

        for i in range(rows):
            for j in range(cols):
                if i == 0 and j == 0:
                    continue

                x, y = cell_xy(j, i)
                board_pos = (j - 1, i - 1)

                # -> prima colonna: rows_targets
                if j == 0:
                    cells.append(
                        Cell(
                            game=self.master,
                            board_pos=board_pos,
                            x=x, y=y,
                            width=cell_width, height=cell_height,
                            text=str(rows_targets[i - 1])
                        )
                    )
                    continue

                # -> prima riga: columns_targets
                if i == 0:
                    cells.append(
                        Cell(
                            game=self.master,
                            board_pos=board_pos,
                            x=x, y=y,
                            width=cell_width, height=cell_height,
                            text=str(cols_targets[j - 1])
                        )
                    )
                    continue

                # -> grid
                cells.append(
                    Cell(
                        game=self.master,
                        board_pos=board_pos,
                        x=x, y=y,
                        width=cell_width, height=cell_height,
                        text=None,
                        command=(lambda j_=j, i_=i: self.master.play(j_ - 1, i_ - 1, None)),
                        activate_keys=["LeftButton"]
                    )
                )

        self._cells = cells
        return self._cells

    # ======== RENDERING ========
    def render_info(self):
        """Raccoglie le info di render di tutte le celle e le unisce in un'unica lista."""
        info = []
        for cell in self.cells:
            info.extend(cell.render_info())
        return info

    # ======== TICK ========
    def tick(self, keys: list[str], cursor_pos: tuple[int, int]):
        """Propaga input e posizione mouse a ogni Cell."""
        for cell in self.cells:
            cell.tick(keys, cursor_pos)
