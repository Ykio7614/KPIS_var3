from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Repository(ABC):
    @abstractmethod
    def load_json(self, path: Path) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def save_json(self, path: Path, payload: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_csv(self, path: Path) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    def save_csv(self, path: Path, rows: list[dict[str, Any]]) -> None:
        raise NotImplementedError
