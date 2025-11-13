from typing import List

from pydantic import BaseModel

from news_core import ArticleMetadata, Event


class ClusterArticle(BaseModel):
    metadata: ArticleMetadata
    vector: List[float]


class ClusterResponse(BaseModel):
    events: List[Event]
