from pydantic import BaseModel, Field


class Source(BaseModel):
    name: str = Field(min_length=1)
    section: str | None = None