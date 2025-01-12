"""Summary model of results for individual user"""

import statistics

from py.utils.utility import DAYS, HOURS
from pydantic import BaseModel, Field


class MemberStats(BaseModel):
    """Template to store results for individual user"""

    messages_sent: int = Field(
        default=0, description="Total number of messages sent by member"
    )
    average_word_count: float = Field(
        default=0.0, description="Average number of words in a message"
    )
    reactions_given: int = Field(
        default=0, description="Total number of reactions given"
    )
    reactions_received: int = Field(
        default=0, description="Total number of reactions received"
    )
    reactions_received_by_sender: dict[str, int] = Field(
        default_factory=dict,
        description="Total number of reactions received, by sender",
    )
    hearts_given: int = Field(
        default=0, description="Total number of hearts / likes received"
    )
    hearts_received: int = Field(
        default=0, description="Total number of hearts / likes received"
    )
    heart_message_ratio: float = Field(
        default=0.0,
        description="Ratio of total hearts / likes recieved to total messages sent",
    )
    hearts_received_by_sender: dict[str, int] = Field(
        default_factory=dict,
        description="Total number ofhearts / likes received, by sender",
    )
    hearts_given_by_receiver: dict[str, int] = Field(
        default_factory=dict,
        description="Total number of hearts / likes given, by receiver",
    )
    dislikes_received: int = Field(
        default=0,
        description="Total number of dislikes (dislike, question) received",
    )
    dislikes_given: int = Field(
        default=0,
        description="Total number of dislikes (dislike, question) given",
    )
    dislikes_received_by_sender: dict[str, int] = Field(
        default_factory=dict,
        description="Total number of dislikes (dislike, question) received, by sender",
    )
    biggest_fan: str = Field(
        default="", description="User who reacted to Member the most with hearts"
    )
    biggest_supporter_of: str = Field(
        default="", description="User who Member gave the most with hearts to"
    )
    most_active_day: str = Field(default="", description="Most common day to post")
    most_active_hour: str = Field(
        default="", description="Most common hour of the day to post"
    )
    images_sent: int = Field(default=0, description="Number of image attachments sent")
    polls_made: int = Field(default=0, description="Number of polls made")
    hours_posted: list[int] = Field(
        default_factory=list, description="Hours of the day the member made posts"
    )
    days_posted: list[int] = Field(
        default_factory=list, description="days of the week member made posts"
    )
    word_count: int = Field(
        default=0, description="The total number of words the user posted"
    )

    def initialize_dicts(self, name_list: list[str]):
        """Fill dictionary fields with zero for each chat member in `name_list`"""
        for name in name_list:
            self.hearts_received_by_sender[name] = 0
            self.hearts_given_by_receiver[name] = 0
            self.reactions_received_by_sender[name] = 0
            self.dislikes_received_by_sender[name] = 0

    def post_time_modes(self):
        """Determine the most common day and hour to post"""
        self.most_active_hour = HOURS[statistics.mode(self.hours_posted)]
        self.most_active_day = DAYS[statistics.mode(self.days_posted)]

    def get_verbosity(self):
        """Determine the avergae word count"""
        self.average_word_count = self.word_count / self.messages_sent

    def get_reaction_superlatives(self):
        """Determine the member's biggest fan and supporter, and their like / post ratio"""

        self.heart_message_ratio = self.hearts_received / self.messages_sent
        biggest_fan = max(
            self.hearts_received_by_sender,
            key=self.hearts_received_by_sender.get,  # pylint: disable=no-member
        )
        self.biggest_fan = (
            f"{biggest_fan} - {self.hearts_received_by_sender[biggest_fan]}"
        )
        biggest_supporter_of = max(
            self.hearts_given_by_receiver,
            key=self.hearts_given_by_receiver.get,  # pylint: disable=no-member
        )
        self.biggest_supporter_of = (f"{biggest_supporter_of} - "
            f"{self.hearts_given_by_receiver[biggest_supporter_of]}")
