from __future__ import annotations

import math
from typing import Iterable, List


def cosine_similarity(vec_a: Iterable[float], vec_b: Iterable[float]) -> float:
    a = list(vec_a)
    b = list(vec_b)
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def normalize(vec: Iterable[float]) -> List[float]:
    vals = list(vec)
    norm = math.sqrt(sum(x * x for x in vals))
    if norm == 0:
        return [0.0 for _ in vals]
    return [x / norm for x in vals]


def jensen_shannon(distribution: Iterable[float]) -> float:
    vals = list(distribution)
    total = sum(vals)
    if not vals or total == 0:
        return 0.0
    probs = [v / total for v in vals]
    m = [0.5 * (p + 1 / len(vals)) for p in probs]
    kld = 0.0
    for p, mm in zip(probs, m):
        if p == 0:
            continue
        kld += 0.5 * p * math.log(p / mm)
    return max(0.0, 1.0 - kld)
