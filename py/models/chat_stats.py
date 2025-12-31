"""Module to contain data on overall chat stats"""

from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field

from py.utils.directories import FileData


class ChatStats(BaseModel):
    """Model to hold data on overall chat stats"""

    num_messages: int = Field(
        default=0, description="The total number of messages sent in the chat"
    )
    average_word_count: float = Field(
        default=0.0, description="Average word count in a message"
    )
    total_reactions: int = Field(
        default=0, description="The total number of reactions performed"
    )
    total_likes: int = Field(
        default=0, description="The total number of likes performed"
    )
    total_dislikes: int = Field(
        default=0, description="The total number of dislikes performed"
    )
    total_image_attachments: int = Field(
        default=0, description="The total number of images posted"
    )
    total_polls: int = Field(default=0, description="The total number of polls made")

def chat_summary_table(chat_stats: ChatStats, output_dir: Path):
    """Create table with most popular messages"""
    headers = ["Stat", "Value"]
    chat_summary = pd.DataFrame(
        columns=headers, index=range(len(ChatStats.model_fields.keys()))
    )
    stats = list(chat_stats.model_dump().values())
    for i, name in enumerate(chat_stats.model_fields.keys()):
        chat_summary.iloc[i] = [name, stats[i]]
    chat_summary.to_csv(output_dir / FileData.chat_summary, sep=",", encoding="utf-8", index=False)

