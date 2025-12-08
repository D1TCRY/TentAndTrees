import unittest
from unittest.mock import Mock, patch

import src.game.core.app as app_module


class AppTest(unittest.TestCase):
    def setUp(self):
        self.get_keys = Mock(return_value=[])
        self.get_mouse = Mock(return_value=(0, 0))
        self.menu = Mock()

        with patch.object(app_module, "MenuManager", return_value=self.menu):
            self.app = app_module.App(
                get_keys_from=self.get_keys,
                get_mouse_pos_from=self.get_mouse
            )

    # ======== INIT E PROPERTIES ========
    def test_init_default_state(self):
        """App deve partire in fase MENU e creare MenuManager."""
        self.assertEqual(self.app.app_phase, app_module.AppPhase.MENU)
        self.assertIs(self.app.menu, self.menu)
        self.assertTrue(callable(self.app.get_keys_from))
        self.assertTrue(callable(self.app.get_mouse_pos_from))

    def test_get_keys_from_type_error(self):
        """get_keys_from deve essere una callable."""
        with patch.object(app_module, "MenuManager", return_value=self.menu):
            with self.assertRaises(TypeError):
                app_module.App(get_keys_from="not-callable", get_mouse_pos_from=self.get_mouse) # type: ignore

    def test_get_mouse_pos_from_type_error(self):
        """get_mouse_pos_from deve essere una callable."""
        with patch.object(app_module, "MenuManager", return_value=self.menu):
            with self.assertRaises(TypeError):
                app_module.App(get_keys_from=self.get_keys, get_mouse_pos_from=123) # type: ignore

    def test_size_setter_type_error(self):
        """size deve essere una tupla (w, h) di lunghezza 2."""
        with self.assertRaises(TypeError):
            self.app.size = 123  # type: ignore
        with self.assertRaises(TypeError):
            self.app.size = (1, 2, 3)  # type: ignore

    # ======== LOAD_GAME ========
    def test_load_game_uses_level_when_given(self):
        """Se il livello è nella lista, usa Game.init_from_level e passa a PLAYING."""
        level = Mock()

        game_obj = Mock()
        gui_obj = Mock()

        with patch.object(app_module, "show_levels", return_value=[level]):
            with patch.object(app_module.Game, "init_from_level", return_value=game_obj) as mock_init:
                with patch.object(app_module, "BoardGameGui", return_value=gui_obj) as mock_gui:
                    self.app.load_game(level)

        mock_init.assert_called_once_with(level)
        mock_gui.assert_called_once()
        self.assertIs(self.app.game, game_obj)
        self.assertIs(self.app.gui, gui_obj)
        self.assertEqual(self.app.app_phase, app_module.AppPhase.PLAYING)

    def test_load_game_random_when_level_not_found(self):
        """Se il livello non esiste, genera una board random e passa a PLAYING."""
        game_obj = Mock()
        gui_obj = Mock()

        with patch.object(app_module, "show_levels", return_value=[]):
            with patch.object(app_module.random, "randint", return_value=10) as mock_rand:
                with patch.object(app_module, "Game", return_value=game_obj) as mock_game:
                    with patch.object(app_module, "BoardGameGui", return_value=gui_obj) as mock_gui:
                        self.app.load_game(level=Mock())

        mock_rand.assert_called_once_with(8, 20)
        mock_game.assert_called_once_with(rows=10, columns=10)
        mock_gui.assert_called_once()
        self.assertIs(self.app.game, game_obj)
        self.assertIs(self.app.gui, gui_obj)
        self.assertEqual(self.app.app_phase, app_module.AppPhase.PLAYING)

    def test_load_game_builds_gui_with_actions(self):
        """load_game deve creare BoardGameGui con la mappa tasti/azioni corretta."""
        game_obj = Mock()
        gui_obj = Mock()

        with patch.object(app_module, "show_levels", return_value=[]):
            with patch.object(app_module.random, "randint", return_value=8):
                with patch.object(app_module, "Game", return_value=game_obj):
                    with patch.object(app_module, "BoardGameGui", return_value=gui_obj) as mock_gui:
                        self.app.load_game(level=None)

        args, kwargs = mock_gui.call_args
        self.assertIs(kwargs["game"], game_obj)

        actions = kwargs["actions"]
        self.assertEqual(actions["LeftButton"], app_module.Action.SKIP)
        self.assertEqual(actions["g"], app_module.Action.PLACE_GRASS)
        self.assertEqual(actions["t"], app_module.Action.PLACE_TENT)
        self.assertEqual(actions["s"], app_module.Action.PLACE_SOLUTION)

    # ======== PLAY_GAME ========
    def test_play_game_esc_returns_to_menu(self):
        """Se 'Esc' viene premuto, torna a MENU e non esegue tick della GUI."""
        self.app.game = Mock()
        self.app.gui = Mock()

        self.app.app_phase = app_module.AppPhase.PLAYING
        self.app.play_game(keys=["Escape"])

        self.assertEqual(self.app.app_phase, app_module.AppPhase.MENU)
        self.app.gui.tick.assert_not_called()

    def test_play_game_sets_game_over_when_finished(self):
        """Se game.finished() è True, passa a GAME_OVER (ma fa comunque tick della GUI per mantenere aggiornata l'ultima immagine)."""
        self.app.game = Mock()
        self.app.gui = Mock()

        self.app.game.finished = Mock(return_value=True)

        self.app.app_phase = app_module.AppPhase.PLAYING
        self.app.play_game(keys=[])

        self.assertEqual(self.app.app_phase, app_module.AppPhase.GAME_OVER)
        self.app.gui.tick.assert_called_once_with()

    def test_play_game_ticks_gui_when_not_finished(self):
        """Se il gioco non è finito, resta in PLAYING e chiama gui.tick()."""
        self.app.game = Mock()
        self.app.gui = Mock()

        self.app.game.finished = Mock(return_value=False)

        self.app.app_phase = app_module.AppPhase.PLAYING
        self.app.play_game(keys=[])

        self.assertEqual(self.app.app_phase, app_module.AppPhase.PLAYING)
        self.app.gui.tick.assert_called_once_with()

    # ======== MENU ========
    def test_load_menu_delegates_to_menu_manager(self):
        """load_menu deve delegare a MenuManager.tick."""
        self.app.menu.tick = Mock()
        self.app.load_menu(keys=["a"], pos=(10.0, 20.0))
        self.app.menu.tick.assert_called_once_with(keys=["a"], cursor_pos=(10.0, 20.0))

    # ======== TICK ========
    def test_tick_calls_load_menu_when_in_menu(self):
        """tick in MENU deve chiamare load_menu con keys e mouse_pos."""
        self.get_keys.return_value = ["k"]
        self.get_mouse.return_value = (1.0, 2.0)
        self.app.load_menu = Mock()

        self.app.app_phase = app_module.AppPhase.MENU
        self.app.tick()

        self.app.load_menu.assert_called_once_with(["k"], (1.0, 2.0))

    def test_tick_calls_load_game_when_start_game(self):
        """tick in START_GAME deve chiamare load_game col livello scelto."""
        level = Mock()
        self.app.menu.selected_level_data = level
        self.app.load_game = Mock()

        self.app.app_phase = app_module.AppPhase.START_GAME
        self.app.tick()

        self.app.load_game.assert_called_once_with(level)

    def test_tick_calls_play_game_when_playing(self):
        """tick in PLAYING deve chiamare play_game(keys)."""
        self.get_keys.return_value = ["x"]
        self.app.play_game = Mock()

        self.app.app_phase = app_module.AppPhase.PLAYING
        self.app.tick()

        self.app.play_game.assert_called_once_with(["x"])

    def test_tick_game_over_resets_menu(self):
        """tick in GAME_OVER deve chiamare set_home e tornare in MENU."""
        self.app.menu.set_home = Mock()

        self.app.app_phase = app_module.AppPhase.GAME_OVER
        self.app.tick()

        self.app.menu.set_home.assert_called_once_with()
        self.assertEqual(self.app.app_phase, app_module.AppPhase.MENU)

    def test_tick_quit_calls_exit(self):
        """tick in QUIT deve chiamare exit()."""
        self.app.app_phase = app_module.AppPhase.QUIT

        with patch("builtins.exit") as mock_exit:
            self.app.tick()

        mock_exit.assert_called_once_with()

if __name__ == "__main__":
    unittest.main()
