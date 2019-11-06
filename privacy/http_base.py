from platform import python_version
from time import sleep
import json
import random
import typing


from requests import models, session, __version__ as req_version


from privacy.util.functional import JsonEncoder
from privacy.util.logging import LoggingClass


class APIException(Exception):
    """Exception used for handling invalid status codes."""
    def __init__(self, response: models.Response) -> None:
        """
        Args:
            :class:`requests.models.Response`
        """
        try:
            error_msg = response.json()["message"]
        except (KeyError, ValueError):
            error_msg = None

        self.code = response.status_code
        self.msg = error_msg
        self.raw = response.content
        super(APIException, self).__init__(
            f"{response.status_code}: {error_msg}"
        )


class Routes:
    """The endpoints and request type exposed by Privacy.com's public api"""
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


class HTTPBaseClient(LoggingClass):
    """The client used for handling api requests and errors."""
    BASE_URL = "https://api.privacy.com/v1/"

    def __init__(
            self, api_key: str = None, debug: bool = False,
            backoff: bool = True) -> None:
        """
        Args:
            api_key:
                An optional string used for authentication.
            debug:
                An optional bool used for toggling the debug api.
            backoff:
                An optional bool used for disabling automatic
                backoff and retry on status codes 5xx or 429.
                Raises :class:`privacy.http_client.APIException` if False.
        """
        self.backoff = backoff
        self.session = session()
        self.session.headers.update({
            "User-Agent": (f"Name-TBD (github TBD {'0.0.1'}) "
                           f"Python/{python_version()} "
                           f"requests/{req_version}")
        })

        if api_key:
            self.session.headers["Authorization"] = "api-key " + api_key

        if debug:
            self.BASE_URL = "https://sandbox.privacy.com/v1/"

    def __call__(
            self, route: typing.List[str],
            url_kwargs: typing.Dict[str, str] = None,
            retries: int = 0, **kwargs) -> models.Response:
        """
        Args:
            route:
                The route for this call from :class:`privacy.http_base.Routes`
            url_kwargs:
                An optional dict of the kwargs to
                be merged with the target url.
            retries:
                An optional int used for handling exponential back off.
            kwargs:
                The kwargs to be passed to :class:`requests.session.request`

        Returns:
            :class:`requests.models.response`
        """
        method, url = route

        # Ensure our custom encoder is used for json data.
        data = kwargs.pop("json", None)
        if data:
            kwargs["data"] = json.dumps(data, cls=JsonEncoder)
            if "headers" not in kwargs:
                kwargs["headers"] = {}

            kwargs["headers"]["content-type"] = "application/json"

        url = self.BASE_URL + url.format(**url_kwargs or {})
        request = self.session.request(method, url, **kwargs)

        if request.status_code < 400:
            return request

        if (not self.backoff or retries == 4 or
                request.status_code < 500 and request.status_code != 429):
            raise APIException(request)
        # TODO: handle other 429s and proper limit

        backoff = self.exponential_backoff(retries)
        retries += 1
        self.log.warning(
            "Request failed with %s, retrying in %s seconds.",
            request.status_code, round(backoff, 4))
        sleep(backoff)
        return self(route, url_kwargs, retries, **kwargs)

    @staticmethod
    def exponential_backoff(retries: int) -> float:
        """
        Generate a time to backoff for before retrying a request.

        Args:
            retries:
                An int of how many times the request has been retried.

        Returns:
            An exponentially random float used for backoff.
        """
        return (2 ** retries) + random.randint(0, 1000) / 1000
