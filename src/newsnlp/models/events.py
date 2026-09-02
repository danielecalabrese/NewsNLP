from datetime import datetime

from pydantic import BaseModel

from newsnlp.models.article import Article


class ArticleCreatedEvent(BaseModel):
    article: Article
    created_at: datetime