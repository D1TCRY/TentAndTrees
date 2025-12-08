from enum import Enum, auto


class MenuPhase(Enum):
    MAIN = auto()

    def __str__(self) -> str:
        return f"<{self.name}>"

    def __repr__(self) -> str:
        return self.__str__()
