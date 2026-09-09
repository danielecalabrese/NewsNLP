from datetime import datetime

from pydantic import BaseModel

from newsnlp.models.article import Article
from newsnlp.models.processed_article import ProcessedArticle


class ArticleCreatedEvent(BaseModel):

    article: Article

    created_at: datetime


class ProcessedArticleEvent(BaseModel):

    article: ProcessedArticle

    processed_at: datetime