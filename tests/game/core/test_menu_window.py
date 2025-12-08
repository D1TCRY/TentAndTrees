import unittest
from unittest.mock import Mock

from src.game.core.menu_window import MenuWindow


class MenuWindowTest(unittest.TestCase):
    def setUp(self):
        self.menu_window = MenuWindow.__new__(MenuWindow)

        self.mock_menu_manager = Mock()
        self.menu_window.menu_manager = self.mock_menu_manager

        self.menu_window._close = Mock()

    # ======== BUTTONS COMMANDS ========
    def test_on_level_selected_sets_level_and_starts_game(self):
        """_on_level_selected deve salvare il livello, chiamare start_game e chiudere la finestra."""
        level = object()

        self.menu_window._on_level_selected(level)

        self.assertIs(self.mock_menu_manager.selected_level_data, level)
        self.mock_menu_manager.start_game.assert_called_once_with()
        self.menu_window._close.assert_called_once_with()

    def test_on_random_calls_on_level_selected_with_none(self):
        """_on_random deve delegare a _on_level_selected(None)."""
        self.menu_window._on_level_selected = Mock()

        self.menu_window._on_random()

        self.menu_window._on_level_selected.assert_called_once_with(None)

    def test_on_quit_calls_menu_manager_quit_and_closes(self):
        """_on_quit deve chiamare menu_manager.quit() e poi chiudere."""
        self.menu_window._on_quit()

        self.mock_menu_manager.quit.assert_called_once_with()
        self.menu_window._close.assert_called_once_with()

    # ======== HELPERS ========
    def test_close_calls_quit_and_destroy(self):
        """_close deve chiamare grab_release, quit e destroy."""
        win = MenuWindow.__new__(MenuWindow)
        win.grab_release = Mock()
        win.quit = Mock()
        win.destroy = Mock()

        win._close()

        win.grab_release.assert_called_once_with()
        win.quit.assert_called_once_with()
        win.destroy.assert_called_once_with()

    def test_close_ignores_grab_release_errors(self):
        """Se grab_release fallisce, _close deve comunque fare quit e destroy."""
        win = MenuWindow.__new__(MenuWindow)
        win.grab_release = Mock(side_effect=Exception("no grab"))
        win.quit = Mock()
        win.destroy = Mock()

        win._close()

        win.grab_release.assert_called_once_with()
        win.quit.assert_called_once_with()
        win.destroy.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
