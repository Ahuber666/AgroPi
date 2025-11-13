from __future__ import annotations

import hashlib
import math
from typing import Iterable, List

from .metrics import normalize


class LocalEncoder:
    """Deterministic encoder used for unit tests and offline fallback."""

    def __init__(self, dim: int = 16):
        self.dim = dim

    def encode(self, texts: Iterable[str]) -> List[List[float]]:
        vectors = []
        for text in texts:
            seed = hashlib.sha256(text.encode()).digest()
            chunk = [b / 255.0 for b in seed[: self.dim]]
            vectors.append(normalize(chunk))
        return vectors

    def encode_single(self, text: str) -> List[float]:
        return self.encode([text])[0]

    @staticmethod
    def cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        denom = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
        if denom == 0:
            return 0.0
        return dot / denom
