from enum import Enum, auto


class AppPhase(Enum):
    MENU = auto()
    START_GAME = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    QUIT = auto()

    def __str__(self) -> str:
        return f"<{self.name}>"

    def __repr__(self) -> str:
        return self.__str__()

