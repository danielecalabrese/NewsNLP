from pydantic import BaseModel, Field


class NLPResult(BaseModel):

    keywords: list[str] = Field(default_factory=list)

    entities: list[str] = Field(default_factory=list)

    sentiment: str | None = None