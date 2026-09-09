from datetime import datetime

from pydantic import BaseModel, Field


class ProcessedArticle(BaseModel):

    article_id: str = Field(min_length=1)

    source_id: str = Field(min_length=1)

    title: str = Field(min_length=1)

    url: str = Field(min_length=1)

    content: str = Field(min_length=1)

    summary: str | None = None

    language: str | None = None

    published_at: datetime | None = None

    processed_at: datetime