from typing import TYPE_CHECKING
import tkinter as tk

# CORE
from .file_management import show_levels, read_settings
if TYPE_CHECKING: from .app import App; from .menu_manager import MenuManager


levels = show_levels()
settings = read_settings()

class MenuWindow(tk.Tk):
    """
        Interfaccia grafica del menu principale.
        - Gestisce graficamente la scelta di un livello.
        - Gestisce la chiusura della finestra.
        - Comunica con il MenuManager e App attraverso metodi e properties.
    """

    def __init__(self, app: "App", menu_manager: "MenuManager", *args, **kwargs) -> None:
        """
            Crea la finestra del menu e la prepara per essere usata come "blocco" principale.

            Qui:
            - centra la finestra
            - imposta la chiusura della finestra
            - la mette in primo piano
            - costruisce tutta la UI (_build_ui())
        """
        super().__init__(*args, **kwargs)
        global settings
        menu_window_settings = settings.get("menu_window", {})

        self.app = app
        self.menu_manager = menu_manager

        self.title("TentsAndTrees | Cecchelani Diego - 386276")
        self.protocol("WM_DELETE_WINDOW", self._on_quit)

        # -> posizione e dimensioni
        self.w, self.h = menu_window_settings.get("width", 420), menu_window_settings.get("height", 520)
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - self.w) // 2
        y = (screen_h - self.h) // 2
        self.geometry(f"{self.w}x{self.h}+{x}+{y}")
        self.resizable(False, False)

        # -> sempre sopra
        self.attributes("-topmost", True)
        self.transient()
        self.grab_set()
        self.focus_force()

        # -> costruisce l'interfaccia grafica
        self._build_ui()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_ui(self) -> None:
        """
            Costruisce graficamente il menu.

            Contiene:
            - titolo e regole
            - lista dei livelli (un bottone per file)
            - due pulsanti in basso: Random e Quit

            La logica è solo di "impaginazione".
            Ogni bottone delega a _on_level_selected / _on_random / _on_quit.
        """
        root = tk.Frame(self, padx=14, pady=14)
        root.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)

        # TITLE
        title = tk.Label(root, text="TENTS AND TREES", font=("Consolas", 24, "bold"))
        title.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # RULES
        rules = tk.Label(root, text="In-menu select: "
                                    "a level to start the game; "
                                    "'Random' to generate a new random level; "
                                    "'Quit' to exit the program. "
                                    "In-game press: 's' to show the solution of the level; "
                                    "'g' to place forced grass cells; "
                                    "'t' to place forced tent cells; "
                                    "'a' to place a hint cell;"
                                    "'Esc' to open the menu."
                                    "Indicator: ✔ resolved; ✘ impossible (needs to be corrected); ⚠ in progress (no obvious error)", font=("Consolas", 8), wraplength=self.w-20)
        rules.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # LEVELS FRAME
        levels_frame = tk.Frame(root)
        levels_frame.grid(row=2, column=0, sticky="nsew")
        levels_frame.grid_columnconfigure(0, weight=1)

        # BUTTONS
        for i, lvl in enumerate(sorted(levels, key=lambda x: x.columns + x.lines)):
            label = f"{lvl.difficulty} {lvl.columns}x{lvl.lines}"
            btn = tk.Button(
                master=levels_frame,
                text=label,
                anchor="center",
                padx=10,
                pady=6,
                command=lambda lv=lvl: self._on_level_selected(lv),
            )
            btn.grid(row=i, column=0, sticky="nsew", pady=3)

        # BOTTOM
        bottom = tk.Frame(root)
        bottom.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        bottom.grid_columnconfigure((0, 1), weight=1)

        # RANDOM + QUIT
        random_btn = tk.Button(bottom, text="Random", command=self._on_random, bg="lightblue", fg="black")
        random_btn.grid(row=0, column=0, sticky="nsew", padx=(0, 5), ipady=5)

        quit_btn = tk.Button(bottom, text="Quit", command=self._on_quit, bg="red", fg="white")
        quit_btn.grid(row=0, column=1, sticky="nsew", padx=(5, 0), ipady=5)

    # ======== BUTTONS COMMANDS ========
    def _on_level_selected(self, level) -> None:
        self.menu_manager.selected_level_data = level
        self.menu_manager.start_game()
        self._close()

    def _on_random(self) -> None:
        level = None
        self._on_level_selected(level)

    def _on_quit(self) -> None:
        self.menu_manager.quit()
        self._close()

    # ======== HELPERS ========
    def _close(self) -> None:
        """Chiude la finestra Tkinter in modo corretto."""
        try:
            self.grab_release()
        except Exception:
            pass
        self.quit()
        self.destroy()

    # ======== PROPERTIES ========
    @property
    def app(self) -> "App":
        return self.__app
    @app.setter
    def app(self, value: "App"):
        self.__app = value

    @property
    def menu_manager(self) -> "MenuManager":
        return self.__menu_manager
    @menu_manager.setter
    def menu_manager(self, value: "MenuManager"):
        self.__menu_manager = value