import unittest
from unittest.mock import Mock, patch, PropertyMock

from src.game.board_game_gui import (
    BoardGameGui,
    init_canvas,
    close_canvas,
    gui_get_released_keys,
    gui_get_mouse_pos,
    clear_canvas,
)
from src.game.state import Action
from src.game.board_game import BoardGame


class DummyGame(BoardGame):
    """Implementazione per soddisfare isinstance(..., BoardGame)."""

    def __init__(self):
        self._play_mock = Mock()
        self._status_mock = Mock(return_value="OK")
        self._progress_mock = Mock(return_value=0)

    # metodi usati da BoardGameGui
    def play(self, r: int, c: int, action):
        self._play_mock(r, c, action)

    def status(self) -> str:
        return self._status_mock()

    def progress(self):
        return self._progress_mock()

    # metodi usati (potenzialmente) da Board/GUI
    def rows(self) -> int:
        return 5

    def cols(self) -> int:
        return 5

    def read(self, r: int, c: int) -> str:
        return "."


class BoardGameGuiTest(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()

    # ======== FREE FUNCTIONS ========
    def test_init_canvas_calls_g2d(self):
        tick = Mock()

        with patch("src.game.board_game_gui.g2d") as g2d:
            init_canvas(tick=tick, size=(10, 20), scale=2, fps=60)

            g2d.init_canvas.assert_called_once_with(size=(10, 20), scale=2)
            g2d.clear_canvas.assert_called_once_with((0, 0, 0))
            g2d.main_loop.assert_called_once_with(tick=tick, fps=60)

    def test_close_canvas_calls_g2d(self):
        with patch("src.game.board_game_gui.g2d") as g2d:
            close_canvas()
            g2d.close_canvas.assert_called_once_with()

    def test_gui_getters_delegate_to_g2d(self):
        with patch("src.game.board_game_gui.g2d") as g2d:
            g2d.current_keys.return_value = []
            g2d.previous_keys.return_value = ["a", "b"]
            g2d.mouse_pos.return_value = (12, 34)

            self.assertEqual(sorted(gui_get_released_keys()), ["a", "b"])
            self.assertEqual(gui_get_mouse_pos(), (12, 34))

    def test_clear_canvas_optional_color(self):
        with patch("src.game.board_game_gui.g2d") as g2d:
            clear_canvas()
            g2d.clear_canvas.assert_called_once_with()

            g2d.clear_canvas.reset_mock()
            clear_canvas((1, 2, 3))
            g2d.clear_canvas.assert_called_once_with((1, 2, 3))

    # ======== INIT / PROPERTIES ========
    def test_init_sets_defaults_without_touching_real_g2d(self):
        with patch("src.game.board_game_gui.clear_canvas") as cc:
            ui = BoardGameGui(game=self.game)

            self.assertIs(ui.game, self.game)
            self.assertIsInstance(ui.actions, dict)
            self.assertEqual(ui.actions, {"LeftButton": ""})
            cc.assert_called()

    def test_game_setter_type_error(self):
        with patch("src.game.board_game_gui.clear_canvas"):
            ui = BoardGameGui(game=self.game)

        with self.assertRaises(TypeError):
            ui.game = "ç°é*§"

    # ======== CUSTOM TICK ========
    def test_tick_sends_actions_to_game_and_ticks_components(self):
        comp1 = Mock()
        comp2 = Mock()
        comp1.tick = Mock()
        comp2.tick = Mock()
        comp1.render_info = Mock(return_value=[])
        comp2.render_info = Mock(return_value=[])

        with patch("src.game.board_game_gui.clear_canvas"), \
             patch("src.game.board_game_gui.gui_get_released_keys", return_value=["g", "x"]), \
             patch("src.game.board_game_gui.gui_get_mouse_pos", return_value=(10, 10)), \
             patch.object(BoardGameGui, "render_guis") as rg, \
             patch.object(BoardGameGui, "gui", new_callable=PropertyMock, return_value=[comp1, comp2]):

            ui = BoardGameGui(game=self.game, actions={"g": Action.PLACE_GRASS})
            ui.tick()

            self.game._play_mock.assert_called_once_with(0, 0, Action.PLACE_GRASS)
            comp1.tick.assert_called_once_with(keys=["g", "x"], cursor_pos=(10, 10))
            comp2.tick.assert_called_once_with(keys=["g", "x"], cursor_pos=(10, 10))
            rg.assert_called_once_with(clear_canvas_=False)

    # ======== RENDERING ========
    def test_render_item_rect_and_text(self):
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
        class TestBoardGameGui(BoardGameGui):
            @property
            def gui(self):
                return self._test_gui

        component = Mock()
        component.render_info = Mock(return_value=[
            {"type": "rect", "pos": (0, 0), "size": (1, 1), "color": (0, 0, 0)},
            {"type": "text", "text": "a", "center": (0, 0), "font_size": 10, "color": (255, 255, 255)},
        ])

        with patch("src.game.board_game_gui.clear_canvas"), \
             patch("src.game.board_game_gui.g2d") as g2d:
            ui = TestBoardGameGui(game=self.game)
            ui._test_gui = [component]

            ui._render_item = Mock()
            ui.render_guis(clear_canvas_=True)

            g2d.clear_canvas.assert_called_once_with((0, 0, 0))
            self.assertEqual(ui._render_item.call_count, 2)


if __name__ == "__main__":
    unittest.main()
