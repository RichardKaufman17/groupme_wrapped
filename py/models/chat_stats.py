"""Module to contain data on overall chat stats"""

from pydantic import BaseModel, Field


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
    total_likes: int = Field(default=0, description="The total number of likes performed")
    total_dislikes: int = Field(
        default=0, description="The total number of dislikes performed"
    )
    total_image_attachments: int = Field(
        default=0, description="The total number of images posted"
    )
    total_polls: int = Field(default=0, description="The total number of polls made")
