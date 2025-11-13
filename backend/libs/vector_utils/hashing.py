from __future__ import annotations

import hashlib
import random
from typing import Iterable, List, Sequence

_HASH_BITS = 64


def _tokenize(text: str) -> List[str]:
    return [tok for tok in text.lower().split() if tok]


def simhash(text: str, hash_bits: int = _HASH_BITS) -> int:
    buckets = [0] * hash_bits
    for token in _tokenize(text):
        digest = int(hashlib.sha1(token.encode()).hexdigest(), 16)
        for bit in range(hash_bits):
            buckets[bit] += 1 if digest & (1 << bit) else -1
    fingerprint = 0
    for i, bucket in enumerate(buckets):
        if bucket >= 0:
            fingerprint |= 1 << i
    return fingerprint


def minhash_signature(tokens: Sequence[str], bands: int = 16) -> List[int]:
    if not tokens:
        return [0] * bands
    rng = random.Random(42)
    hashes = [int(hashlib.md5(tok.encode()).hexdigest(), 16) for tok in tokens]
    signature = []
    for _ in range(bands):
        perm = list(hashes)
        rng.shuffle(perm)
        signature.append(min(perm))
    return signature
