"""Configuration of analysis parameters"""

import json
import logging
from datetime import datetime
from typing import Self

from py.utils.utility import validate_json_input
from py.utils.directories import FileData
from pydantic import BaseModel, Field, model_validator, field_validator

LOG = logging.getLogger(__name__)


class ChatKeywords(BaseModel):
    """Information for keyword search"""

    aliases: list[str] = Field(
        description="A list of grouped keywords to search for the number of occurances"
    )
    name: str = Field(
        default="", description="The name to represent the set of keywords in plots"
    )

    @field_validator("aliases")
    @classmethod
    def asliases(cls, values: list[str]) -> list[str]:
        """Validate aliases"""
        return [alias.lower() for alias in values]

    @model_validator(mode="after")
    def set_name(self) -> Self:
        """Set the name if it was not specified"""
        if not self.name:
            self.name = self.aliases[0].strip()

        return self


class AnalysisConfig(BaseModel):
    """Basemodel class to store analysis parameters"""

    start_date: datetime | float | None = Field(
        default=None,
        description="Start date of messages to fetch, as datetime (%Y-%m-%d %H:%M:%S) or timestamp",
    )
    end_date: datetime | float | None = Field(
        default=None,
        description="End date of messages fetch, as datetime (%Y-%m-%d %H:%M:%S) or timestamp",
    )
    message_request_limit: int = Field(
        default=200,
        description="Amount of messages to grab in a single request",
        le=200,
        ge=1,
    )
    chat_name: str = Field(
        default="Group Chat",
        description="Name of groupchat to be referred to in figures",
    )
    chat_keywords: list[ChatKeywords] | None = Field(
        default=None, description="A list of chat keywords to analyze"
    )
    num_messages_rank: int = Field(
        default=10, description="Number of messages to rank, ie: 10 most popular"
    )
    exclude_copilot: bool = Field(
        default = True,
        description = "Whether copilot AI chatmember should be included in stats"
    )

    @model_validator(mode="after")
    def set_earliest_date(self) -> Self:
        """Define earliest date based on user_input"""
        if self.start_date is not None and isinstance(self.start_date, datetime):
            self.start_date = datetime.timestamp(self.start_date)
        if self.end_date is not None and isinstance(self.end_date, datetime):
            self.end_date = datetime.timestamp(self.end_date)
        return self


def read_analysis_config(filename: str | None) -> AnalysisConfig:
    """Function to read analysis config file"""

    if filename is not None:
        analysis_file = FileData.analysis_configs / validate_json_input(filename)
        LOG.info("Using analysis parameters defined in %s", analysis_file)
        with open(analysis_file, encoding="utf-8") as json_file:
            return AnalysisConfig.model_validate_json(json.dumps(json.load(json_file)))
    LOG.warning("No analysis config input, analysis will use default parameters")
    return AnalysisConfig()
