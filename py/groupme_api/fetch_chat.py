"""Module to obatain groupchat data"""

import json
import logging
from pathlib import Path
from typing import Iterable

import requests
from requests import Response

from py.groupme_api.request_utils import (
    ENDPOINT,
    HEADERS,
    GroupMeException,
    NotModifiedException,
    StatusCode,
)
from py.models.analysis_config import AnalysisConfig

LOG = logging.getLogger(__name__)

class FetchChat:
    """Class with medthods necessary for fetching GroupMe chat"""

    def __init__(
        self, chat_id: str, acces_token: str, output_file: Path, config: AnalysisConfig
    ):
        self.chat_id = chat_id
        self.access_token = acces_token
        self.output_file = output_file
        self.config = config

        self.endpoint: str
        self.headers: dict[str, str]
        self.format_request()

    def fetch_chat(self):
        """Method to fetch group chat contents"""
        params = {"limit": self.config.message_request_limit}
        message_iterator = self.iterate_messages(params)
        message_count = 0
        batch = 1
        with open(self.output_file, "w", encoding="utf-8") as file:
            file.write("[\n")
            while message := next(message_iterator, None):
                if (
                    self.config.end_date is None or
                    message["created_at"] < self.config.end_date
                ):
                    LOG.debug("Writing message %s", message["id"])
                    LOG.debug(
                        "Message fetched %d / %d of batch %d",
                        message_count + 1,
                        self.config.message_request_limit,
                        batch,
                    )
                    file.write("\t")
                    file.write(json.dumps(message))
                    file.write(",\n")
                message_count += 1
                if message_count == self.config.message_request_limit:
                    params["before_id"] = message["id"]
                    message_iterator = self.iterate_messages(params)
                    message_count = 0
                    LOG.info("Completed message batch %d", batch)
                    batch += 1
            file.write("]")
        self.remove_trailing_comma()

    def format_request(self):
        """Format header and endpoint"""
        self.endpoint = ENDPOINT.format(self.chat_id)
        self.headers = HEADERS
        self.headers["X-Access-Token"] = self.access_token
        self.headers["Referer"].format(self.chat_id)

    def send_request(self, params: dict[str, int]) -> Response:
        """Send request for chat messages and validate it"""
        response = requests.get(
            self.endpoint, params=params, headers=self.headers, timeout=10
        )
        LOG.debug("Request Status Code: %d", response.status_code)
        StatusCode.validate_request(response)
        return response

    def iterate_messages(self, params: dict[str, int]) -> Iterable[dict | None]:
        """Generator to query groupme messages and iterate through them"""
        try:
            response = self.send_request(params)
            for message in response.json()["response"]["messages"]:
                if (
                    self.config.start_date is not None
                    and message["created_at"] < self.config.start_date
                ):
                    LOG.info(
                        "No more messages after timestamp: %r",
                        self.config.start_date,
                    )
                    yield None
                yield message
        except NotModifiedException as e:
            LOG.info(e)
            yield None
        except (
            GroupMeException,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException,
        ) as e:
            LOG.error(e)
            LOG.error("Error occured, fetch of chat messages will not continue")
            yield None

    def remove_trailing_comma(self):
        """Remove last comma in groupme message formatted json file"""
        with open(self.output_file, "r", encoding="utf-8") as f:
            text = f.readlines()
            text[-2] = text[-2].rsplit(",", maxsplit=1)[0] + "\n"
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.writelines(text)
