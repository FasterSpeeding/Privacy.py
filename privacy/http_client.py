"""The client used for handling raw requests."""
from platform import python_version
from time import sleep
import json
import random
import typing


import requests


from privacy.util import GIT, VERSION
from privacy.util.json import CustomJsonEncoder
from privacy.util.logging import LoggingClass


class APIException(Exception):
    """Exception used for handling invalid status codes."""
    def __init__(self, response: requests.models.Response):
        """
        Args:
            response (requests.models.Response): The response object.
        """
        error_msg = None
        if response.headers.get("Content-Type") == "application/json":
            try:
                error_msg = response.json()["message"]
            except (KeyError, json.decoder.JSONDecodeError):
                pass

        self.code = response.status_code
        self.msg = error_msg
        self.raw = response.content
        super().__init__(
            f"{response.status_code}: {error_msg}"
        )


class Routes:
    """The endpoints exposed by Privacy.com's public api"""
    CARDS_LIST = ("GET", "card")
    TRANSACTIONS_LIST = ("GET", "transaction/{approval_status}")

    # PREMIUM
    CARDS_CREATE = ("POST", "card")
    CARDS_MODIFY = ("PUT", "card")
    HOSTED_CARD_UI_GET = ("GET", "embed/card")

    # SANDBOX
    SIMULATE = "simulate/"
    SIMULATE_AUTH = ("POST", SIMULATE + "authorize")
    SIMULATE_VOID = ("POST", SIMULATE + "void")
    SIMULATE_CLEARING = ("POST", SIMULATE + "clearing")
    SIMULATE_RETURN = ("POST", SIMULATE + "return")


class HTTPClient(LoggingClass):
    """
    The client used for handling http requests and errors.

    Attributes:
        BASE_URL (string): The url used as the base for all http calls.
        backoff (bool): Toggles retries and exponential backoff.
        session (requests.session): The request session used for http calls.
    """
    BASE_URL: str = "https://api.privacy.com/v1/"
    RETRIES: int = 5
    session: requests.session = None

    def __init__(self, api_key: str, backoff: bool = True, sandboxed: bool = False):
        """
        Args:
            api_key (string): The key used for authentication.
            backoff (bool, optional): Used to disable automatic retry on status codes 5xx or 429.
                Client will raise `privacy.http_client.APIException` instead of retrying if False.
            sandboxed (bool, optional): Used for switching to Privacy's sandboxed http.
        """
        self.backoff = backoff
        self.session = requests.session()
        self.session.headers.update({
            "Authorization": "api-key " + api_key,
            "User-Agent": (f"Privacy.py (github {GIT} {VERSION}) "
                           f"Python/{python_version()} requests/{requests.__version__}")
        })

        if sandboxed:
            self.BASE_URL = "https://sandbox.privacy.com/v1/"

    def __call__(
            self, route: typing.List[str],
            url_kwargs: typing.Dict[str, str] = None,
            retries: int = 0, **kwargs) -> requests.models.Response:
        """
        Args:
            route (privacy.http_client.Routes): The route for this call.
            url_kwargs (dict, optional): The kwargs to be merged with the target url.
            retries (int, optional): Used for handling exponential back off.
            kwargs: The kwargs to be passed to `requests.session.request`.

        Returns:
            response (requests.models.response): The response objects.

        Raises:
            APIException (privacy.http_client.APIException): On status code 5xx and certain 429s.
        """
        # Make sure headers is pre-set for upcoming checks.
        if "headers" not in kwargs:
            kwargs["headers"] = {}

        # Ensure the custom json encoder is used for pydantic objects.
        json_data = kwargs.pop("json", None)
        if json_data:
            kwargs["data"] = CustomJsonEncoder.dumps(json_data)
            kwargs["headers"]["content-type"] = "application/json"

        method, url = route
        url = self.BASE_URL + url.format(**url_kwargs or {})
        response = self.session.request(method, url, **kwargs)

        if response.status_code < 400:
            return response

        # Raise general http errors.
        if response.status_code < 500 and response.status_code != 429:
            raise APIException(response)

        # Handle backoff on 429s and 5xx.
        if not self.backoff or retries == self.RETRIES - 1 or not self.should_backoff(response):
            raise APIException(response)

        backoff = self.exponential_backoff(retries)
        retries += 1
        self.log.warning(
            "Request failed with %s, retrying in %s seconds.",
            response.status_code, round(backoff, 4))
        sleep(backoff)
        return self(route, url_kwargs, retries, **kwargs)

    @staticmethod
    def exponential_backoff(retries: int) -> float:
        """
        Generate a time to backoff for before retrying a request.

        Args:
            retries (int): How many times the request has been retried.

        Returns:
            float: An exponentially random float used for backoff.
        """
        return (2 ** retries) + random.randint(0, 1000) / 1000

    @staticmethod
    def should_backoff(response: requests.models.Response):
        """
        Work out if the client should retry after a 5xx or 429.

        Args:
             response (requests.models.Response): The response object.
        """
        # Note right now, if something in-between us and the http returns a 429, this will raise an exception.
        # Always retry on a 5xx.
        if response.status_code >= 500:
            return True

        # Don't try to decode json content if content-type is not json.
        if response.headers.get("Content-Type") != "application/json":
            return False

        # Attempt to get error message and if not present, give up.
        try:
            msg = response.json()["message"]
        except (KeyError, json.decoder.JSONDecodeError):
            return False

        return msg == "Rate limited, too many requests per second"
