"""The client used for handling raw requests."""
from platform import python_version
from json.decoder import JSONDecodeError
from time import sleep
import random
import typing


from requests import models, session, __version__ as req_version


from privacy.util import GIT, VERSION
from privacy.util.logging import LoggingClass


class APIException(Exception):
    """Exception used for handling invalid status codes."""
    def __init__(self, response: models.Response):
        """
        Args:
            response (requests.models.Response): The response object.
        """
        error_msg = None
        if response.headers.get("Content-Type") == "application/json":
            try:
                error_msg = response.json()["message"]
            except (KeyError, JSONDecodeError):
                pass

        self.code = response.status_code
        self.msg = error_msg
        self.raw = response.content
        super(APIException, self).__init__(
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
    The client used for handling api requests and errors.

    Attributes:
        BASE_URL (string): The url used as the base for all api calls.
        backoff (bool): Toggles retries and exponential backoff.
        session (requests.session): The request session used for api calls.
    """
    BASE_URL = "https://api.privacy.com/v1/"
    RETRIES = 5

    def __init__(
            self, api_key: str = None, sandboxed: bool = False,
            backoff: bool = True):
        """
        Args:
            api_key (string, optional): The key used for authentication.
            sandboxed (bool, optional): Used for switching to Privacy's sandboxed api.
            backoff (bool, optional): Used to disable automatic retry on status codes 5xx or 429.
                Client will raise `privacy.http_client.APIException` instead of retrying if False.
        """
        self.backoff = backoff
        self.session = session()
        self.session.headers.update({
            "User-Agent": (f"Privacy.py (github {GIT} {VERSION}) "
                           f"Python/{python_version()} requests/{req_version}")
        })

        if api_key:
            self.session.headers["Authorization"] = "api-key " + api_key

        if sandboxed:
            self.BASE_URL = "https://sandbox.privacy.com/v1/"

    def __call__(
            self, route: typing.List[str],
            url_kwargs: typing.Dict[str, str] = None,
            retries: int = 0, **kwargs) -> models.Response:
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
            TypeError: If api authentication key is unset.
        """
        # Make sure headers is pre-set for upcoming checks.
        if "headers" not in kwargs:
            kwargs["headers"] = {}

        # Ensure that passed auth key is formatted correctly or api key is already set in sesssion headers.
        if "Authorization" in kwargs["headers"]:
            kwargs["headers"]["Authorization"] = "api-key " + kwargs["headers"]["Authorization"]
        elif "Authorization" not in self.session.headers:
            raise TypeError("Authentication key is unset.")

        # Ensure the custom json encoder is used for pydantic objects.
        if hasattr(kwargs.get("json"), "json"):
            kwargs["data"] = kwargs.pop("json").json()
            kwargs["headers"]["content-type"] = "application/json"

        method, url = route
        url = self.BASE_URL + url.format(**url_kwargs or {})
        response = self.session.request(method, url, **kwargs)

        if response.status_code < 400:
            return response

        # Raise general api errors.
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
    def should_backoff(response: models.Response):
        """
        Work out if the client should retry after a 5xx or 429.

        Args:
             response (requests.models.Response): The response object.
        """
        # Note right now, if something inbetween us and the api returns a 429, this will raise an exception.
        # Always retry on a 5xx.
        if response.status_code >= 500:
            return True

        # Don't try to decode json content if content-type is not json.
        if response.headers.get("Content-Type") != "application/json":
            return False

        # Attempt to get error message and if not present, give up.
        try:
            msg = response.json()["message"]
        except (KeyError, JSONDecodeError):
            return False

        return msg == "Rate limited, too many requests per second"
