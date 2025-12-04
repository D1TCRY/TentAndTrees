import unittest
from unittest.mock import Mock, patch

from src.game.gui.board import Board


class BoardTest(unittest.TestCase):
    def setUp(self):
        self.master = Mock()
        self.master.cols.return_value = 2
        self.master.rows.return_value = 2
        self.master.columns_targets = [1, 0]
        self.master.rows_targets = [0, 1]
        self.master.play = Mock()

        self.board = Board(
            master=self.master,
            x=0, y=0,
            width=100, height=100,
            padding=2
        )

    def test_cells_are_built_once_and_reused(self):
        """cells deve costruire la griglia solo la prima volta e poi riusarla."""
        with patch("src.game.gui.board.Cell") as CellMock:
            c1 = self.board.cells
            c2 = self.board.cells

        self.assertIs(c1, c2)

    def test_cells_count_is_expected(self):
        """Con cols=2, rows=2: griglia (3x3) meno angolo (0,0) => 8 celle."""
        with patch("src.game.gui.board.Cell") as CellMock:
            cells = self.board.cells

        self.assertEqual(len(cells), 8)

    def test_cells_targets_have_text(self):
        """Prima riga/colonna devono creare celle con testo dei target."""
        with patch("src.game.gui.board.Cell") as CellMock:
            _ = self.board.cells

            calls = CellMock.call_args_list
            texts = [kwargs.get("text") for _, kwargs in calls]

            # colonne targets: 2 celle in alto (escluso angolo) -> "1" e "0"
            self.assertIn("1", texts)
            self.assertIn("0", texts)

    def test_grid_cell_command_calls_master_play(self):
        """Una cella interna deve avere command che chiama master.play(x, y, None)."""
        with patch("src.game.gui.board.Cell") as CellMock:
            _ = self.board.cells

            # -> cerco una call di griglia: text=None e ha command
            grid_kwargs = None
            for args, kwargs in CellMock.call_args_list:
                if kwargs.get("text") is None and kwargs.get("command") is not None:
                    grid_kwargs = kwargs
                    break

            self.assertIsNotNone(grid_kwargs)

            # -> eseguo il comando e verifico che chiami play(..., None)
            cmd = grid_kwargs["command"]
            cmd()

        self.master.play.assert_called()
        args = self.master.play.call_args[0]
        self.assertEqual(args[2], None)

    def test_render_info_collects_all_cells(self):
        """render_info deve unire render_info() di tutte le celle."""
        # -> evito di dipendere dal vero Cell: imposto _cells a mano
        c1 = Mock()
        c1.render_info.return_value = [{"type": "rect"}]
        c2 = Mock()
        c2.render_info.return_value = [{"type": "text"}]
        self.board._cells = [c1, c2]

        out = self.board.render_info()

        self.assertEqual(out, [{"type": "rect"}, {"type": "text"}])

    def test_tick_propagates_to_all_cells(self):
        """tick deve chiamare tick(keys, cursor_pos) su ogni cella."""
        c1 = Mock()
        c2 = Mock()
        self.board._cells = [c1, c2]

        self.board.tick(keys=["LeftButton"], cursor_pos=(10, 10))

        c1.tick.assert_called_once_with(["LeftButton"], (10, 10))
        c2.tick.assert_called_once_with(["LeftButton"], (10, 10))


if __name__ == "__main__":
    unittest.main()
