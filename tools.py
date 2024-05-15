from enum import Enum, auto


def log(message: str) -> None:
    print(f"[LOG] {message}")


class ChatbotCycleResult(Enum):
    OK = auto()
    RETRY = auto()
    INVALID = auto()
    UNRELATED = auto()
    EXIT = auto()
