"""Vector math helpers used across embeddings, deduper, and ranker."""

from .metrics import cosine_similarity, jensen_shannon, normalize
from .hashing import minhash_signature, simhash
from .embedding import LocalEncoder

__all__ = [
    "cosine_similarity",
    "jensen_shannon",
    "normalize",
    "minhash_signature",
    "simhash",
    "LocalEncoder",
]
