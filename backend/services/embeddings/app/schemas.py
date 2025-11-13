from datetime import datetime
from typing import List

from pydantic import BaseModel

from news_core import ArticleContent


class EmbeddingVector(BaseModel):
    article_id: str
    vector: List[float]
    generated_at: datetime


class EmbeddingRequest(BaseModel):
    articles: List[ArticleContent]
