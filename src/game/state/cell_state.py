from enum import Enum, auto


class CellState(Enum):
    EMPTY = auto()
    TREE = auto()
    GRASS = auto()
    TENT = auto()
    OUT = auto()

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return self.__str__()
