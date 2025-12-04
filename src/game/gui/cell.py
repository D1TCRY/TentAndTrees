from collections.abc import Callable
from .button import Button
from .color import Color

from ..core.file_management import read_settings

SCALE = read_settings().get("scale", 1)
SETTINGS = read_settings()


class Cell(Button):
    def __init__(self,
                 game,
                 board_pos: tuple[int, int],
                 name_id: str = "Cell",
                 x: float = 0,
                 y: float = 0,
                 width: float = 80,
                 height: float = 24,
                 text: str | None = None,
                 text_size: int = 10,
                 text_color: Color = (248, 248, 248),
                 background_color: Color = (48, 48, 48),
                 hover_color: Color | None = (48, 48, 108),
                 pressed_color: Color | None = (48, 64, 208),
                 fixed: bool = True,
                 enabled: bool = True,
                 command: Callable[[], None] | None = None,
                 activate_keys: list[str] | None = None) -> None:
        """
            Una singola cella cliccabile della board.

            È un Button specializzato che:
            - mantiene riferimento al gioco a cui appartiene (game)
            - ricorda la propria coordinata sulla griglia (board_pos)
            - prende testo e colori da settings.json in base allo stato della cella (EMPTY, TREE, TENT, ...)

            Se passi text manualmente (ad esempio per i numeri target) ha priorità
            e non viene sovrascritto dallo stato del gioco.
        """

        global SETTINGS

        self.cooldown = 0
        self.cooldown_time = 5

        self.game = game
        self.board_pos = board_pos

        state = str(self.game.get_cell_state(*self.board_pos))
        self.text = SETTINGS.get(state, {}).get("text", "Error") if text is None else text

        super().__init__(name_id=name_id,
                         x=x, y=y, width=width, height=height,
                         text=self.text, text_size=text_size,
                         text_color=text_color, background_color=background_color, hover_color=hover_color,
                         pressed_color=pressed_color, fixed=fixed,
                         enabled=enabled, command=command, activate_keys=activate_keys)

        self.changed = True
        self._last_render_signature = None

    def tick(self, keys: list[str], cursor_pos: tuple[float, float]) -> None:
        """
            Aggiorna la cella a ogni frame.
            - gestisce un piccolo cooldown per evitare click multipli
            - ricalcola testo e colori leggendo lo stato attuale dal game (e da SETTINGS)
            - aggiorna hover e gestisce l'input (handle_keys)
        """
        global SETTINGS

        if self.cooldown > 0:
            self.cooldown -= 1
            return

        self.text_size = (20 / 39) * min(self.width, self.height) # 20/39 è una proporzione utile per determinare la dimensione del testo

        state = str(self.game.get_cell_state(*self.board_pos))

        if self.game.inside(*self.board_pos):
            self.text = SETTINGS.get(state, {}).get("text", "Error")

        self.background_color = tuple(SETTINGS.get(state, {}).get("background_color", (48, 48, 48)))
        self.hover_color = tuple(SETTINGS.get(state, {}).get("hover_color", (48, 48, 108)))
        self.pressed_color = tuple(SETTINGS.get(state, {}).get("pressed_color", (48, 64, 208)))

        self.update_hover(cursor_pos)
        self.handle_keys(keys)

    def invoke(self) -> None:
        """Esegue il command associato alla cella (se abilitata), con un cooldown."""

        if self.cooldown > 0:
            return

        self.cooldown = self.cooldown_time

        if self.enabled and self.command is not None:
            self.command()

        # -> dopo un'azione il render deve aggiornarsi
        self._last_render_signature = None


    # ========== RENDERING ==========
    def _render_signature(self):
        """
        Restituisce una firma hashabile di tutto ciò che influisce sul disegno.
        Se questa firma non cambia, render_info deve tornare [].
        """
        x, y = self.x, self.y
        width, height = self.width, self.height

        if not self.enabled:
            base = self.background_color
            bg_color = tuple(int(c * 0.5) for c in base)
        elif self.pressed:
            bg_color = self.pressed_color
        elif self.hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.background_color

        def rgba_of(c):
            return c.rgba if hasattr(c, "rgba") else tuple(c)

        return (
            x, y, width, height,
            str(self.text), float(self.text_size),
            bool(self.enabled), bool(self.hovered), bool(self.pressed),
            rgba_of(bg_color),
            rgba_of(self.text_color),
        )

    def render_info(self) -> list[dict]:
        """Ritorna la lista di istruzioni di disegno per questa cella"""
        sig = self._render_signature()

        if sig == self._last_render_signature:
            return []

        self._last_render_signature = sig

        x, y = self.x, self.y
        width, height = self.width, self.height
        center_x = x + width / 2
        center_y = y + height / 2

        if not self.enabled:
            base = self.background_color
            bg_color = tuple(int(c * 0.5) for c in base)
        elif self.pressed:
            bg_color = self.pressed_color
        elif self.hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.background_color

        return [
            {
                "type": "rect",
                "color": bg_color.rgba,
                "pos": (x, y),
                "size": (width, height)
            },
            {
                "type": "text",
                "color": self.text_color.rgba,
                "text": str(self.text),
                "center": (center_x, center_y),
                "font_size": self.text_size
            }
        ]

    @property
    def board_pos(self) -> tuple[int, int]:
        return self.__board_pos
    @board_pos.setter
    def board_pos(self, new: tuple[int, int]) -> None:
        self.__board_pos = new
        # -> cambiare cella significa cambiare cosa disegna
        if hasattr(self, "_last_render_signature"):
            self._last_render_signature = None

    @property
    def game(self):
        return self.__game
    @game.setter
    def game(self, new) -> None:
        self.__game = new
        if hasattr(self, "_last_render_signature"):
            self._last_render_signature = None
