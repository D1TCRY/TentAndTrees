from __future__ import annotations

from collections.abc import Callable
from typing import Any

# STATE
from .state import Action

# GUI
from .gui import Board, GUIComponent, Text, Bar

# G2D
from src.g2d_lib import g2d

# GAME
from .board_game import BoardGame

# CORE
from .core.file_management import read_settings


settings = read_settings()
SIZE = settings.get("size", 430)


def init_canvas(
    tick: Callable[[], None],
    size: tuple[int, int] | None = None,
    scale: float = 1,
    fps: int = 30
) -> None:
    """Inizializza il canvas e avvia il loop principale."""
    g2d.init_canvas(size=size, scale=scale)
    g2d.clear_canvas((0, 0, 0))
    g2d.main_loop(tick=tick, fps=fps)
def close_canvas() -> None:
    g2d.close_canvas()
def gui_get_current_keys():
    return g2d.current_keys()
def gui_get_released_keys():
    return list(set(gui_get_previous_keys()) - set(gui_get_current_keys()))
def gui_get_mouse_pos():
    return g2d.mouse_pos()
def gui_get_previous_keys() -> list[str]:
    return g2d.previous_keys()

def clear_canvas(color: tuple[int, int, int] | None = None) -> None:
    g2d.clear_canvas(color) if color is not None else g2d.clear_canvas()



class BoardGameGui:
    def __init__(
        self,
        game: BoardGame,
        actions: dict[str, Any] | None = None
    ):
        global settings
        clear_canvas(tuple(settings.get("board_game_gui", {}).get("background_color", [0,0,0]))) # type: ignore

        self.game = game
        self.actions = actions or {"LeftButton": ""}

    def tick(self) -> None:
        """
            Tick "custom" della GUI (quello usato dal tuo progetto, non la versione default).

            Ogni frame:
            - legge tasti e mouse da g2d
            - se un tasto è mappato in actions, invia l'azione al game ('g', 't', 's')
            - lascia ai componenti GUI (Board, Cell) la gestione di hover/click e logica locale
            - infine disegna solo ciò viene realmente modificato per efficienza, senza ripulire lo sfondo
              (il clear viene chiamato una volta a creazione del livello)
        """
        keys = gui_get_released_keys()
        pos = gui_get_mouse_pos()

        for key in keys:
            if key in self.actions:
                self.game.play(0, 0, self.actions[key])

        for component in self.gui:
            if hasattr(component, "tick"):
                component.tick(keys=keys, cursor_pos=pos)

        self.render_guis(clear_canvas_=False)

    # ======== RENDERING ========
    def _render_item(self, item: dict[str, Any]) -> None:
        """Prende un singolo oggetto di render (un dizionario) e lo traduce in chiamate g2d."""
        type_ = item.get("type")
        color = item.get("color")

        if color is not None:
            g2d.set_color(color)

        if type_ == "rect":
            pos = item.get("pos")
            size = item.get("size")
            if pos is not None and size is not None:
                g2d.draw_rect(pos=pos, size=size)

        elif type_ == "text":
            text = item.get("text")
            center = item.get("center")
            font_size = item.get("font_size")
            if text is not None and center is not None and font_size is not None:
                g2d.draw_text(text=text, center=center, size=font_size)

    def render_guis(self, clear_canvas_: bool | None = None) -> None:
        """Disegna tutti i componenti GUI registrati in self.gui."""
        if clear_canvas_:
            g2d.clear_canvas((0, 0, 0))

        for gui_component in self.gui:
            info = gui_component.render_info()  # type: ignore
            for item in info:
                self._render_item(item)

    # ======== PROPERTIES ========
    @property
    def gui_board(self) -> Board:
        """Crea (solo la prima volta) e ritorna la Board principale. È inizializzata in modo "lazy".
        La board rappresenta l'intero campo di gioco effettivo."""
        global settings, SIZE

        if not hasattr(self, f"_{self.__class__.__name__}__gui_board"):
            self.__gui_board = Board(
                master=self.game,
                x=0, y=0,
                width=SIZE, height=SIZE*settings.get("board_game_gui", {}).get("board", {}).get("height%", 0.95),
                padding=settings.get("board_game_gui", {}).get("board", {}).get("padding", 2),
            )
        return self.__gui_board
    @property
    def gui_stats(self) -> Bar:
        """Crea e ritorna la barra in basso con stato e progresso."""
        global settings, SIZE
        board_settings = settings.get("board_game_gui", {}).get("board", {})
        stats_settings = settings.get("board_game_gui", {}).get("stats", {})

        board_height = SIZE*board_settings.get("height%", 0.95)
        background_color = tuple(settings.get("board_game_gui", {}).get("background_color", (0,0,0)))

        return Bar(
                   name_id="gui_stats",
                   x=0, y=board_height, width=SIZE, height=SIZE-board_height,
                   text=self.game.status(), text_size=stats_settings.get("text_size", 30), text_color=tuple(stats_settings.get("text_color", [248, 248, 248])), # type: ignore
                   background_color=background_color, bar_color=tuple(stats_settings.get("progress_bar_color", (48,96,48))), # type: ignore
                   max_value=1, value=lambda game=self.game: game.progress() if game.progress() is not None else 0,
                   padding=stats_settings.get("progress_padding", 2), fixed=True
        )
    @property
    def gui(self) -> list[GUIComponent]:
        return [self.gui_board, self.gui_stats]

    @property
    def game(self) -> BoardGame:
        return self.__game
    @game.setter
    def game(self, new: BoardGame) -> None:
        if not isinstance(new, BoardGame):
            raise TypeError("game must be a BoardGame instance")
        self.__game = new

    @property
    def actions(self) -> dict[str, Action | str]:
        return self.__actions
    @actions.setter
    def actions(self, value: dict[str, Action | str]) -> None:
        if not isinstance(value, dict):
            raise TypeError("actions must be a dictionary")
        self.__actions = value
