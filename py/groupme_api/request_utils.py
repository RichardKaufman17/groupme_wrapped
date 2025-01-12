"""Request Data, Status Code and Exception Definitions"""

from enum import IntEnum
from requests import Response


ENDPOINT = "https://api.groupme.com/v3/groups/{}/messages"
HEADERS = {
            "Accept": "application/json, text/javascript",
            "Accept-Charset": "ISO-8859-1,utf-8",
            "Accept-Language": "en-US",
            "Content-Type": "application/json",
            "Origin": "https://web.groupme.com",
            "Referer": "https://web.groupme.com/groups/{}",
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 "
            "(KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22"),
            "X-Access-Token": "{}",
        }

class StatusCode(IntEnum):
    """Enums for status codes"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    NOT_MODIFIED = 304
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    ENHANCE_YOUR_CALM = 420
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503

    @classmethod
    def validate_request(cls, response: Response):
        """Validate request result"""
        status = response.status_code
        if status == cls.NOT_MODIFIED.value:
            raise NotModifiedException("End of chat reached, no more messages to query")
        if status not in [cls.OK.value, cls.CREATED.value, cls.NO_CONTENT.value]:
            raise GroupMeException(f"Bad response: status code {status}")

class GroupMeException(Exception):
    """Exception when GroupMe request fails"""

class NotModifiedException(Exception):
    """Exception when no content is fetched"""
