from enum import Enum, auto


def log(message: str) -> None:
    print(f"\033[32m[LOG]\033[0m {message}")


class ChatbotCycleResult(Enum):
    OK = auto()
    RETRY = auto()
    INVALID = auto()
    UNRELATED = auto()
    EXIT = auto()
