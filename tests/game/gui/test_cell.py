import unittest
from unittest.mock import Mock, patch

from src.game.gui.cell import Cell


class CellTest(unittest.TestCase):
    def setUp(self):
        self.game = Mock()
        self.game.get_cell_state.return_value = "EMPTY"
        self.game.inside.return_value = True

    def test_init_uses_settings_text_when_text_is_none(self):
        """Se text non è passato, lo prende da SETTINGS in base allo stato."""
        fake_settings = {
            "EMPTY": {"text": ".", "background_color": (1, 2, 3), "hover_color": (4, 5, 6), "pressed_color": (7, 8, 9)}
        }

        with patch("src.game.gui.cell.SETTINGS", fake_settings):
            cell = Cell(game=self.game, board_pos=(0, 0), text=None)

        self.assertEqual(cell.text, ".")

    def test_init_text_argument_has_priority(self):
        """Se passo text manualmente (tipo target), non viene sovrascritto dallo stato."""
        fake_settings = {"EMPTY": {"text": "X"}}

        with patch("src.game.gui.cell.SETTINGS", fake_settings):
            cell = Cell(game=self.game, board_pos=(0, 0), text="7")

        self.assertEqual(cell.text, "7")

    def test_tick_decreases_cooldown_and_returns(self):
        """Se cooldown > 0, tick deve solo decrementare e non fare altro."""
        cell = Cell(game=self.game, board_pos=(0, 0), text="X")
        cell.cooldown = 2

        # -> se tick continua, chiamerebbe update_hover/handle_keys
        cell.update_hover = Mock()
        cell.handle_keys = Mock()

        cell.tick(keys=["LeftButton"], cursor_pos=(10.0, 10.0))

        self.assertEqual(cell.cooldown, 1)
        cell.update_hover.assert_not_called()
        cell.handle_keys.assert_not_called()

    def test_tick_updates_colors_and_calls_button_handlers(self):
        """tick deve aggiornare colori e chiamare update_hover + handle_keys."""
        fake_settings = {
            "EMPTY": {
                "text": ".",
                "background_color": (10, 10, 10),
                "hover_color": (20, 20, 20),
                "pressed_color": (30, 30, 30),
            }
        }

        with patch("src.game.gui.cell.SETTINGS", fake_settings):
            cell = Cell(game=self.game, board_pos=(0, 0), text=None)

            cell.update_hover = Mock()
            cell.handle_keys = Mock()

            cell.tick(keys=["LeftButton"], cursor_pos=(5.0, 6.0))

        # -> i colori vengono normalizzati in RGBA (alpha default = 255)
        self.assertEqual(cell.background_color.rgba, (10, 10, 10, 255))
        self.assertEqual(cell.hover_color.rgba, (20, 20, 20, 255))
        self.assertEqual(cell.pressed_color.rgba, (30, 30, 30, 255))

        cell.update_hover.assert_called_once_with((5.0, 6.0))
        cell.handle_keys.assert_called_once_with(["LeftButton"])

    def test_invoke_runs_command_and_sets_cooldown(self):
        """invoke deve chiamare command se enabled e impostare il cooldown."""
        cmd = Mock()
        cell = Cell(game=self.game, board_pos=(0, 0), command=cmd, text="X")
        cell.enabled = True
        cell.cooldown = 0

        cell.invoke()

        cmd.assert_called_once_with()
        self.assertEqual(cell.cooldown, cell.cooldown_time)

    def test_invoke_does_nothing_during_cooldown(self):
        """Se cooldown > 0, invoke deve ignorare il click."""
        cmd = Mock()
        cell = Cell(game=self.game, board_pos=(0, 0), command=cmd, text="X")
        cell.cooldown = 3

        cell.invoke()

        cmd.assert_not_called()
        self.assertEqual(cell.cooldown, 3)

    def test_render_info_is_cached(self):
        """Se la firma non cambia, render_info deve tornare [] alla seconda chiamata."""
        cell = Cell(game=self.game, board_pos=(0, 0), text="X")

        cell.text_color = (1, 1, 1)
        cell.background_color = (2, 2, 2)
        cell.hover_color = (3, 3, 3)
        cell.pressed_color = (4, 4, 4)

        out1 = cell.render_info()
        out2 = cell.render_info()

        self.assertTrue(isinstance(out1, list))
        self.assertEqual(out2, [])

    def test_board_pos_resets_render_cache(self):
        """Cambiare board_pos deve invalidare la cache del render."""
        cell = Cell(game=self.game, board_pos=(0, 0), text="X")
        cell._last_render_signature = ("fake",)

        cell.board_pos = (1, 1)

        self.assertIsNone(cell._last_render_signature)

    def test_game_setter_resets_render_cache(self):
        """Cambiare game deve invalidare la cache del render."""
        cell = Cell(game=self.game, board_pos=(0, 0), text="X")
        cell._last_render_signature = 1e19,

        cell.game = Mock()

        self.assertIsNone(cell._last_render_signature)


if __name__ == "__main__":
    unittest.main()
