import unittest
from unittest.mock import Mock, patch

from src.game.board_game_gui import (
    BoardGameGui,
    init_canvas,
    close_canvas,
    gui_get_current_keys,
    gui_get_mouse_pos,
    clear_canvas,
)
from src.game.state import Action
from src.game.board_game import BoardGame


class BoardGameGuiTest(unittest.TestCase):
    def setUp(self):
        self.game = Mock(spec=BoardGame)
        self.game.play = Mock()
        self.game.finished = Mock(return_value=False)
        self.game.status = Mock(return_value="OK")
        self.game.rows = Mock(return_value=5)
        self.game.cols = Mock(return_value=5)
        self.game.read = Mock(return_value=".")

    # ======== FREE FUNCTIONS ========
    def test_init_canvas_calls_g2d(self):
        """init_canvas deve inizializzare e avviare il main loop di g2d."""
        tick = Mock()

        with patch("src.game.board_game_gui.g2d") as g2d:
            init_canvas(tick=tick, size=(10, 20), scale=2, fps=60)

            g2d.init_canvas.assert_called_once_with(size=(10, 20), scale=2)
            g2d.clear_canvas.assert_called_once_with((0, 0, 0))
            g2d.main_loop.assert_called_once_with(tick=tick, fps=60)

    def test_close_canvas_calls_g2d(self):
        """close_canvas deve delegare a g2d.close_canvas()."""
        with patch("src.game.board_game_gui.g2d") as g2d:
            close_canvas()
            g2d.close_canvas.assert_called_once_with()

    def test_gui_getters_delegate_to_g2d(self):
        """gui_get_current_keys e gui_get_mouse_pos devono leggere direttamente da g2d."""
        with patch("src.game.board_game_gui.g2d") as g2d:
            g2d.current_keys.return_value = ["a", "b"]
            g2d.mouse_pos.return_value = (12, 34)

            self.assertEqual(gui_get_current_keys(), ["a", "b"])
            self.assertEqual(gui_get_mouse_pos(), (12, 34))

    def test_clear_canvas_optional_color(self):
        """clear_canvas con/senza colore deve chiamare g2d.clear_canvas correttamente."""
        with patch("src.game.board_game_gui.g2d") as g2d:
            clear_canvas()
            g2d.clear_canvas.assert_called_with()

            g2d.clear_canvas.reset_mock()
            clear_canvas((1, 2, 3))
            g2d.clear_canvas.assert_called_with((1, 2, 3))

    # ======== INIT / PROPERTIES ========
    def test_init_sets_defaults_without_touching_real_g2d(self):
        """__init__ non deve esplodere in test anche se g2d non ha un canvas reale."""
        with patch("src.game.board_game_gui.clear_canvas") as cc:
            ui = BoardGameGui(game=self.game, use_default=False)

            self.assertIs(ui.game, self.game)
            self.assertFalse(ui.use_default)
            self.assertIsInstance(ui.actions, dict)
            self.assertIsInstance(ui.annots, dict)
            cc.assert_called()

    def test_init_use_default_calls_update_buttons_but_mocked(self):
        """Se use_default True, __init__ deve chiamare update_buttons (mockato)."""
        with patch("src.game.board_game_gui.clear_canvas"), patch.object(BoardGameGui, "update_buttons") as ub:
            ui = BoardGameGui(game=self.game, use_default=True)

            ub.assert_called_once_with()
            self.assertTrue(ui.use_default)
            self.assertIs(ui.game, self.game)

    def test_game_setter_type_error(self):
        """game deve essere un BoardGame."""
        with patch("src.game.board_game_gui.clear_canvas"):
            ui = BoardGameGui(game=self.game)

        with self.assertRaises(TypeError):
            ui.game = "not-a-game"  # type: ignore

    # ======== CUSTOM TICK ========
    def test_tick_custom_sends_actions_to_game_and_ticks_components(self):
        """tick custom: invia azioni per i tasti mappati e chiama tick/render."""
        class TestableBoardGameGui(BoardGameGui):
            @property
            def gui(self):
                return self._test_gui

        comp1 = Mock()
        comp2 = Mock()
        comp1.tick = Mock()
        comp2.tick = Mock()
        comp1.render_info = Mock(return_value=[])
        comp2.render_info = Mock(return_value=[])

        with patch("src.game.board_game_gui.clear_canvas"), \
             patch("src.game.board_game_gui.gui_get_current_keys", return_value=["g", "x"]), \
             patch("src.game.board_game_gui.gui_get_mouse_pos", return_value=(10, 10)), \
             patch.object(BoardGameGui, "render_guis") as rg:

            ui = TestableBoardGameGui(
                game=self.game,
                actions={"g": Action.PLACE_GRASS},
                use_default=False
            )
            ui._test_gui = [comp1, comp2]

            ui.tick()

            self.game.play.assert_called_once_with(0, 0, Action.PLACE_GRASS)
            comp1.tick.assert_called_once()
            comp2.tick.assert_called_once()
            rg.assert_called_once_with(clear_canvas_=False)

    def test_tick_custom_delegates_to_default_tick_when_use_default(self):
        """Se use_default True, tick deve chiamare default_tick e fermarsi."""
        with patch("src.game.board_game_gui.clear_canvas"), patch.object(BoardGameGui, "default_tick") as dt, \
             patch.object(BoardGameGui, "update_buttons"):
            ui = BoardGameGui(game=self.game, use_default=True)
            ui.tick()
            dt.assert_called_once_with()

    # ======== RENDERING ========
    def test_render_item_rect_and_text(self):
        """_render_item deve tradurre i dict in draw_rect/draw_text."""
        with patch("src.game.board_game_gui.g2d") as g2d, patch("src.game.board_game_gui.clear_canvas"):
            ui = BoardGameGui(game=self.game)

            ui._render_item({"type": "rect", "color": (1, 2, 3), "pos": (0, 0), "size": (10, 10)})
            g2d.set_color.assert_called_with((1, 2, 3))
            g2d.draw_rect.assert_called_with(pos=(0, 0), size=(10, 10))

            g2d.set_color.reset_mock()
            ui._render_item({"type": "text", "color": (9, 9, 9), "text": "hi", "center": (5, 5), "font_size": 12})
            g2d.set_color.assert_called_with((9, 9, 9))
            g2d.draw_text.assert_called_with(text="hi", center=(5, 5), size=12)

    def test_render_guis_calls_render_item_for_each_component_item(self):
        """render_guis deve ciclare sui componenti e renderizzare i loro item."""
        class TestableBoardGameGui(BoardGameGui):
            @property
            def gui(self):
                return self._test_gui

        comp = Mock()
        comp.render_info = Mock(return_value=[
            {"type": "rect", "pos": (0, 0), "size": (1, 1), "color": (0, 0, 0)},
            {"type": "text", "text": "a", "center": (0, 0), "font_size": 10, "color": (255, 255, 255)},
        ])

        with patch("src.game.board_game_gui.clear_canvas"), \
             patch("src.game.board_game_gui.g2d") as g2d:
            ui = TestableBoardGameGui(game=self.game)
            ui._test_gui = [comp]

            ui._render_item = Mock()

            ui.render_guis(clear_canvas_=True)

            g2d.clear_canvas.assert_called_once_with((0, 0, 0))
            self.assertEqual(ui._render_item.call_count, 2)

    # ======== DEFAULT TICK (SIMPLE) ========
    def test_default_tick_closes_when_finished(self):
        """Se game.finished() True, default_tick deve alertare e chiudere canvas."""
        self.game.finished.return_value = True

        with patch("src.game.board_game_gui.clear_canvas"), patch("src.game.board_game_gui.g2d") as g2d:
            g2d.mouse_pos.return_value = (0, 0)

            ui = BoardGameGui(game=self.game)
            ui.default_tick()

            g2d.alert.assert_called_once_with("OK")
            g2d.close_canvas.assert_called_once_with()

    def test_default_tick_escape_closes_canvas(self):
        """Se viene rilasciato Escape, default_tick deve chiudere il canvas."""
        with patch("src.game.board_game_gui.clear_canvas"), patch("src.game.board_game_gui.g2d") as g2d:
            g2d.mouse_pos.return_value = (0, 0)
            g2d.previous_keys.return_value = ["Escape"]
            g2d.current_keys.return_value = []

            ui = BoardGameGui(game=self.game)
            ui.default_tick()

            g2d.close_canvas.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
