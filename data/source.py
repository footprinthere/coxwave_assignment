from typing import Optional, overload
from abc import ABC, abstractmethod

import re
import pickle


def load_source_data(path: str) -> dict[str, str]:
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data


def preprocess_content(content: str) -> str:
    # Remove '\xa0' and '\ufeff'
    content = content.replace("\xa0", " ").replace("\ufeff", "")
    # Remove consecutive whitespaces
    content = re.sub(r"\s+", " ", content)

    # Remove tail message
    TAIL = "위 도움말이 도움이 되었나요?"
    if (tail_idx := content.rfind(TAIL)) != -1:
        content = content[:tail_idx]

    return content


class BaseSourceProcessor(ABC):

    @overload
    def __init__(self, *, data: dict[str, str], data_path: None = ...) -> None: ...

    @overload
    def __init__(self, *, data: None = ..., data_path: str) -> None: ...

    def __init__(
        self,
        *,
        data: Optional[dict[str, str]] = None,
        data_path: Optional[str] = None,
    ):
        if data is None:
            if data_path is None:
                raise ValueError("Either `data` or `data_path` should be provided.")
            data = load_source_data(data_path)
        self.data = data

        self._preprocess_content()

    @abstractmethod
    def process_entry(self, title: str, content: str) -> str: ...

    def process_data(self) -> list[str]:
        return [
            self.process_entry(title, content) for title, content in self.data.items()
        ]

    def parse_for_metadata(self) -> list[dict[str, str]]:
        return [
            {"title": title, "content": content} for title, content in self.data.items()
        ]

    def _preprocess_content(self) -> None:
        self.data = {
            title: preprocess_content(content) for title, content in self.data.items()
        }


class ConcatSourceProcessor(BaseSourceProcessor):
    """Simply concatenate title and content."""

    def process_entry(self, title: str, content: str) -> str:
        return f"{title} {content}"


class TitleOnlySourceProcessor(BaseSourceProcessor):
    """Use only title."""

    def process_entry(self, title: str, content: str) -> str:
        return title
