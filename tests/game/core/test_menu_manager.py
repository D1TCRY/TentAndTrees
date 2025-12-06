import unittest
from unittest.mock import Mock, patch

from src.game.core.menu_manager import MenuManager
from src.game.state import AppPhase, MenuPhase


class MenuManagerTest(unittest.TestCase):
    def setUp(self):
        self.app = Mock()
        self.mm = MenuManager(self.app)

    # ======== INIT ========
    def test_init_default_state(self):
        """MenuManager deve partire in MAIN, con selected_level_data None e menu chiuso."""
        self.assertIs(self.mm.master, self.app)
        self.assertEqual(self.mm.phase, MenuPhase.MAIN)
        self.assertIsNone(self.mm.selected_level_data)
        self.assertIsInstance(self.mm.levels, list)
        self.assertFalse(self.mm._menu_open)

    # ======== FROM MENU_WINDOW ========
    def test_start_game_sets_app_phase_and_resets_menu_phase(self):
        """start_game deve portare l'app in START_GAME e rimettere il menu in MAIN."""
        self.mm.phase = MenuPhase.MAIN
        self.mm.start_game()

        self.assertEqual(self.app.app_phase, AppPhase.START_GAME)
        self.assertEqual(self.mm.phase, MenuPhase.MAIN)

    def test_quit_sets_app_phase_quit(self):
        """quit deve impostare l'app in QUIT."""
        self.mm.quit()
        self.assertEqual(self.app.app_phase, AppPhase.QUIT)

    # ======== TICK / MENU OPEN ========
    def test_tick_opens_menu_only_when_main_and_not_open(self):
        """tick deve aprire il menu solo quando è in MAIN e non è già aperto."""
        self.mm.open_level_menu = Mock()

        self.mm.phase = MenuPhase.MAIN
        self.mm._menu_open = False
        self.mm.tick(keys=[], cursor_pos=(0.0, 0.0))

        self.mm.open_level_menu.assert_called_once_with()

        # se è già aperto, non deve richiamarlo
        self.mm.open_level_menu.reset_mock()
        self.mm._menu_open = True
        self.mm.tick(keys=[], cursor_pos=(0.0, 0.0))

        self.mm.open_level_menu.assert_not_called()

    def test_open_level_menu_sets_menu_open_true_then_false(self):
        """open_level_menu deve settare _menu_open True durante il mainloop e poi rimetterlo False."""
        with patch("src.game.core.menu_manager.MenuWindow") as MW:
            fake_win = Mock()
            MW.return_value = fake_win

            self.mm._menu_open = False
            self.mm.open_level_menu()

            MW.assert_called_once_with(app=self.app, menu_manager=self.mm)
            fake_win.mainloop.assert_called_once_with()
            self.assertFalse(self.mm._menu_open)

    # ======== PROPERTIES ========
    def test_phase_type_error(self):
        """phase deve accettare solo MenuPhase."""
        with self.assertRaises(TypeError):
            self.mm.phase = "MAIN"  # type: ignore

    def test_set_home_resets_phase(self):
        """set_home deve riportare la fase del menu a MAIN."""
        self.mm.phase = MenuPhase.MAIN
        self.mm.set_home()
        self.assertEqual(self.mm.phase, MenuPhase.MAIN)


if __name__ == "__main__":
    unittest.main()
