from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CategoryName:
    value: str

    def __post_init__(self) -> None:
        v = self.value.strip()
        if not v:
            raise ValueError("CategoryName must not be empty.")
        if len(v) > 50:
            raise ValueError("CategoryName must be <= 50 characters.")
        object.__setattr__(self, "value", v)

    def __str__(self) -> str:
        return self.value


_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")

@dataclass(frozen=True, slots=True)
class HexColor:
    """Accepts #RRGGBB or #RGB."""
    value: str

    def __post_init__(self) -> None:
        if not _HEX_RE.match(self.value):
            raise ValueError("HexColor must be #RRGGBB or #RGB.")
