from enum import Enum, auto


class Action(Enum):
    NONE = auto()
    PLACE_TENT = auto()
    PLACE_GRASS = auto()
    PLACE_SOLUTION = auto()
    SKIP = auto()
    PLACE_HINT = auto()

    def __str__(self) -> str:
        return f"<{self.name}>"

    def __repr__(self) -> str:
        return self.__str__()

