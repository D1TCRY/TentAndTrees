from __future__ import annotations
import random
from collections.abc import Callable

# G2D
from src.g2d_lib import g2d

# GAME
from ..board_game_gui import BoardGameGui, gui_get_mouse_pos, gui_get_released_keys, init_canvas, clear_canvas

# CORE
from .game import Game
from .file_management import *
from .menu_manager import MenuManager

# GUI
from ..gui import GUIComponent

# STATE
from ..state import *

settings = read_settings()
SCALE = settings.get("scale", 1)
FPS = settings.get("fps", 30)
SIZE = settings.get("size", 430)


class App(object):
    def __init__(self,
                 get_keys_from: Callable[[], list[str]],
                 get_mouse_pos_from: Callable[[], tuple[float | int, float | int]]) -> None:

        self.get_keys_from = get_keys_from
        self.get_mouse_pos_from = get_mouse_pos_from

        self.app_phase = AppPhase.MENU

        self.menu = MenuManager(self)

    # ======= METHODS ========
    def load_game(self, level: Level | None = None) -> None:
        """
            Prepara e avvia una nuova partita.

            Se viene passato un Level e quel livello esiste tra quelli caricati da disco, lo usa.
            Altrimenti ne genera uno: sceglie una dimensione casuale e genera una board valida.

            Crea:
            - self.game (logica)
            - self.gui (interfaccia g2d), con la mappa tasti/azioni
            Alla fine sposta l'app in AppPhase.PLAYING.
        """
        levels = show_levels()

        if level in levels:
            self.game = Game.init_from_level(level)
        else:
            side = random.randint(8, 20)
            self.game = Game(rows=side, columns=side)

        self.gui = BoardGameGui(game=self.game,
                                actions={
                                    "LeftButton": Action.SKIP,
                                    "g": Action.PLACE_GRASS,
                                    "t": Action.PLACE_TENT,
                                    "s": Action.PLACE_SOLUTION
                                })

        self.app_phase = AppPhase.PLAYING

    def play_game(self, keys: list[str]) -> None:
        """
            Gestisce un frame di gioco quando in PLAYING.

            - Escape -> torna al menu (senza chiudere il programma).
            - Se per qualche motivo game/gui non esistono, rientra al menu per sicurezza.
            - Se il livello è risolto, passa a GAME_OVER.
            - Altrimenti delega tutto alla GUI (tick), che legge input e disegna.
        """
        if "Escape" in keys:
            self.app_phase = AppPhase.MENU
            return

        if not (hasattr(self, "game") and hasattr(self, "gui")):
            self.app_phase = AppPhase.MENU
            return

        if self.game.finished():
            self.app_phase = AppPhase.GAME_OVER

        self.gui.tick()

    def load_menu(self, keys: list[str], pos: tuple[float, float]) -> None:
        """Gestisce un frame quando nel menu. In pratica delega al MenuManager."""
        self.menu.tick(keys=keys, cursor_pos=pos)

    def tick(self) -> None:
        """
            Viene chiamato a ogni frame dal main_loop di g2d.

            Se app_phase è:
            - MENU: apre/gestisce il menu
            - START_GAME: crea game + gui
            - PLAYING: fa avanzare la partita
            - GAME_OVER: resetta il menu e torna alla home
            - QUIT: esce dal processo
        """
        match self.app_phase:
            case AppPhase.MENU:
                self.load_menu(self.keys, self.mouse_pos)
            case AppPhase.START_GAME:
                self.load_game(self.menu.selected_level_data)
            case AppPhase.PLAYING:
                self.play_game(self.keys)
            case AppPhase.GAME_OVER:
                self.menu.set_home()
                self.app_phase = AppPhase.MENU
            case AppPhase.QUIT:
                exit()
            case _:
                self.app_phase = AppPhase.MENU

    # ======== PROPERTIES ========
    @property
    def get_keys_from(self) -> Callable[[], list[str]]:
        return self.__get_keys_from
    @get_keys_from.setter
    def get_keys_from(self, value: Callable[[], list[str]]) -> None:
        if not callable(value):
            raise TypeError("get_keys_from must be a callable")
        self.__get_keys_from: Callable[[], list[str]] = value

    @property
    def get_mouse_pos_from(self) -> Callable[[], tuple[float | int, float | int]]:
        return self.__get_mouse_pos_from
    @get_mouse_pos_from.setter
    def get_mouse_pos_from(self, value: Callable[[], tuple[float | int, float | int]]) -> None:
        if not callable(value):
            raise TypeError("get_mouse_pos_from must be a callable")
        self.__get_mouse_pos_from: Callable[[], tuple[float | int, float | int]] = value

    @property
    def keys(self) -> list[str]:
        return self.get_keys_from()

    @property
    def mouse_pos(self) -> tuple[float | int, float | int]:
        return self.get_mouse_pos_from()

    @property
    def size(self) -> tuple[int, int]:
        return self.__size
    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        if not isinstance(value, tuple) or len(value) != 2:
            raise TypeError("size must be a tuple of length 2")
        self.__size: tuple[int, int] = value

    @property
    def app_phase(self) -> AppPhase:
        return self.__app_status
    @app_phase.setter
    def app_phase(self, new: AppPhase) -> None:
        self.__app_status = new


def main() -> None:
    """Entry point"""
    global SCALE, FPS
    app = App(get_keys_from=gui_get_released_keys, get_mouse_pos_from=gui_get_mouse_pos)
    init_canvas(tick=app.tick, size=(SIZE, SIZE), scale=SCALE, fps=FPS)
