from typing import TYPE_CHECKING

# CORE
if TYPE_CHECKING: from .app import App
from .file_management import show_levels
from .level import Level
from .menu_window import MenuWindow

# STATE
from ..state import AppPhase
from ..state import MenuPhase




class MenuManager:
    """
    Manager logico del menu:
    - apre una finestra tkinter quando richiesto
    - memorizza il livello scelto (selected_level_data)
    - aggiorna MenuPhase
    - comunica all'App modificandone app_phase
    """

    def __init__(self, master: "App") -> None:
        self.master = master
        self.phase = MenuPhase.MAIN
        self.selected_level_data = None
        self.levels = show_levels()

        self._menu_open = False

    # ======== FROM MENU_WINDOW ========
    def start_game(self) -> None:
        self.master.app_phase = AppPhase.START_GAME
        self.phase = MenuPhase.MAIN

    def quit(self) -> None:
        self.master.app_phase = AppPhase.QUIT

    # ======== METHODS ========
    def open_level_menu(self) -> None:
        """
        Apre la finestra tkinter e aspetta una scelta.
        La finestra stessa imposterà selected_level_data e chiamerà start_game/quit.
        """
        self._menu_open = True
        win = MenuWindow(app=self.master, menu_manager=self)
        win.mainloop()
        self._menu_open = False

    def set_home(self) -> None:
        self.phase = MenuPhase.MAIN

    # ======== TICK ========
    def tick(self, keys: list[str], cursor_pos: tuple[float, float]) -> None:
        if self.phase is MenuPhase.MAIN and not self._menu_open:
            self.open_level_menu()

    # ======== PROPERTIES ========
    @property
    def master(self) -> "App":
        return self.__master
    @master.setter
    def master(self, value: "App") -> None:
        self.__master = value

    @property
    def phase(self) -> MenuPhase:
        return self.__phase
    @phase.setter
    def phase(self, value: MenuPhase) -> None:
        if not isinstance(value, MenuPhase):
            raise TypeError("phase must be a MenuPhase")
        self.__phase = value

    # -> from menu_window
    @property
    def selected_level_data(self) -> Level | None:
        return self.__selected_level_data
    @selected_level_data.setter
    def selected_level_data(self, value: Level | None) -> None:
        self.__selected_level_data = value

    @property
    def levels(self):
        return self.__levels
    @levels.setter
    def levels(self, value) -> None:
        self.__levels = value
