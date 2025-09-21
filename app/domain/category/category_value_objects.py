from __future__ import annotations

import re
from dataclasses import dataclass

_MAX_LENGTH = 50


@dataclass(frozen=True, slots=True)
class CategoryName:
    value: str

    def __post_init__(self) -> None:
        v = self.value.strip()
        if not v:
            raise ValueError("CategoryName must not be empty.")
        if len(v) > _MAX_LENGTH:
            raise ValueError("CategoryName must be <= 50 characters.")
        object.__setattr__(self, "value", v)

    def __str__(self) -> str:
        return self.value
