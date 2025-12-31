"""Template to store data on popular or unpopular messages"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field


class MessageSuperlative(BaseModel):
    """Basemodel class to store information on message superlative"""

    poster: str = Field(description="The poster of the message")
    created_at: datetime = Field(description="Date when the post was made")
    text: str | None = Field(default=None, description="Text of message")
    image_attachment: str | None = Field(
        default=None, description="Link to Image attachment"
    )
    likers: list[str] = Field(
        default_factory=list, description="List of users who reacted to the message"
    )
    total_likes: int = Field(
        default=0, ge=0, description="The total number of reactions"
    )

def popular_message_table(messages: list[MessageSuperlative], output_file: Path):
    """Create table with most popular messages"""
    headers = list(MessageSuperlative.model_fields.keys())
    messages_ranked = pd.DataFrame(columns=headers, index=range(len(messages)))
    for i, message in enumerate(messages):
        messages_ranked.iloc[i] = list(message.model_dump().values())
    messages_ranked.to_csv(output_file, sep=",", encoding="utf-8", index=False)
