from __future__ import annotations

import math
import re
from typing import Protocol


class ReadingTimeCalculator(Protocol):
    def calculate_minutes(self, text: str) -> int | None:
        ...


class WordCountReadingTimeCalculator:
    def __init__(self, words_per_minute: int = 200, minimum_minutes: int = 1) -> None:
        self._words_per_minute = words_per_minute
        self._minimum_minutes = minimum_minutes

    def calculate_minutes(self, text: str) -> int | None:
        words = len(re.findall(r'\b\w+\b', text, flags=re.UNICODE))
        if words == 0:
            return None
        return max(self._minimum_minutes, math.ceil(words / self._words_per_minute))

