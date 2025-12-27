"""Template for message data requested from groupme API"""

from enum import Enum

from pydantic import BaseModel, Field


class AttachmentType(Enum):
    """Types of attachments"""

    REPLY = "reply"
    IMAGE = "image"
    POLL = "poll"
    EVENT = "event"
    MENTIONS = "mentions"
    VIDEO = "video"
    EMOJI = "emoji"
    FILE = "file"
    LOACTION = "location"
    LINKED_IMAGE = "linked_image"
    AUDIO = "audio"
    COPILOT = "copilot"


class ReactionEmojis(Enum):
    """Emoji types for likes and dislikes"""

    HEART = "\u2764\ufe0f"
    QUESTION = "\u2753"
    LIKE = "\ud83d\udc4d"
    DISLIKE = "\ud83d\udc4e"
    FIRE = "\ud83d\udd25"


class ChatMessage(BaseModel):
    """BaseModel class for individual chat message"""

    class Reaction(BaseModel):
        """Location info template"""

        type: str = Field(description="Type of encoding or reaction")
        user_ids: list[str] = Field(
            description="User Ids that reacted with reaction type"
        )
        code: str = Field(default="", description="Reaction code")
        pack_id: str | None = None
        pack_index: str | None = None

    class Attachment(BaseModel):
        """Template for attachments in message"""

        type: AttachmentType
        url: str | None = None
        user_id: str | None = None
        reply_id: str | None = None
        base_reply_id: str | None = None
        poll_id: str | None = None
        loci: list[list[int]] | None = None
        user_ids: list[str] | None = None
        event_id: str | None = None
        view: str | None = None
        preview_url: str | None = None
        charmap: list[list[int]] | None = None
        placeholder: str | None = None
        file_id: str | None = None
        name: str | None = None
        lat: str | None = None
        long: str | None = None
        peaks: str | None = None
        duration: int | None = None

    id: int
    attachments: list[Attachment]
    source_guid: str
    created_at: int
    user_id: str
    group_id: str
    avatar_url: str | None
    name: str
    text: str | None
    favorited_by: list[str]
    reactions: list[Reaction] | None = None


LIKES = [
    reaction.value
    for reaction in [ReactionEmojis.HEART, ReactionEmojis.LIKE, ReactionEmojis.FIRE]
]
DISLIKES = [
    reaction.value for reaction in [ReactionEmojis.DISLIKE, ReactionEmojis.QUESTION]
]
