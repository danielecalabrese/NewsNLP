from pydantic import BaseModel, Field


class FeedConfiguration(BaseModel):
    name: str = Field(min_length=1)
    url: str = Field(min_length=1)
    enabled: bool = True