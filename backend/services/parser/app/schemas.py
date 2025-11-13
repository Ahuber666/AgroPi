from pydantic import BaseModel

from news_core import ArticleMetadata


class ParseRequest(BaseModel):
    article: ArticleMetadata
    html: str
