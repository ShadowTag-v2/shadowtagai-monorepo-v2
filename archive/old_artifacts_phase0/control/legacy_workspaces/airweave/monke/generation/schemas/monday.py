from pydantic import BaseModel, Field


class MondayItem(BaseModel):
    token: str = Field(description="Verification token to embed in item name or text column")
    name: str = Field(description="Item name; should contain the token")
    note: str | None = Field(default=None, description="Short note to put into a text column")
    comments: list[str] = Field(default_factory=list, description="Optional updates/comments")
