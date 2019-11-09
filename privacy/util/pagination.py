"""Used for handling paginated api endpoints."""
from enum import Enum
from typing import Any, Iterable


class Direction(Enum):
    """An enum of the directions used by `privacy.util.pagination.PaginatedResponse`"""
    UP = 0
    DOWN = 1


class PaginatedResponse:
    """
    Used for automatically iterating through paginated api endpoints.

    Attributes:
        client (privacy.api_client.APIClient): The client used for api calls.
        direction (privacy.util.pagination.Direction): The direction for crawling through pages.
        limit (int, optional): The amount of object(s) that this will
            return during iteration (unset for unlimited).
        pymodel (privacy.schema.CustomBase): The dataclass this wraps
            and will be returning objects as during iteration.
        total_entries (int): The total entries according to retrieved data.
        total_pages (int): The total pages according to retrieved data.
        args: Args passed through to `requests.session.request`.
        kwargs: Kwargs passed through to `requests.session.request`.
    """
    total_entries = None
    total_pages = None
    _list = None

    def __init__(
            self, pymodel, client,
            *args, direction: Direction = None,
            limit: int = None, **kwargs: Any) -> None:
        """
        Args:
            pymodel (privacy.schema.CustomBase): The dataclass that this will be
                returning objects as during iteration.
            client (privacy.api_client.APIClient): The api client used for making
                requests to crawl through pages.
            *args: Args passed through to `requests.session.request`.
            direction (privacy.util.pagination.Direction, optional): The direction that this
                will crawl through pages.
            limit (int, optional): Used to limit how many object(s) this
                will return while being iterated through.
            **kwargs: Kwargs passed through to `requests.session.request`.

        Raises:
            TypeError: If invalid pagination direction is supplied.
        """
        self.client = client
        self.direction = direction or Direction.UP
        self.limit = limit
        self.pymodel = pymodel

        # Handle request args and kwargs
        if "params" in kwargs:
            self._page = kwargs["params"].pop("page", None)
        else:
            kwargs["params"] = {}
        self.args = args
        self.kwargs = kwargs

        self.get_starting_point()
        self._buffer = []

    def __iter__(self) -> Iterable:
        return self

    def __next__(self) -> Any:
        if self.limit == 0:
            self.reset()
            raise StopIteration()

        if not self._buffer:
            self.crawl_data()
            if not self._buffer:
                self.reset()
                raise StopIteration()

        if self.limit:
            self.limit -= 1
        return self._buffer.pop()

    def __repr__(self) -> str:
        return f"<PaginatedResponse({self.pymodel.__name__})>"

    @property
    def cached_list(self) -> list:
        """A simple cached list property."""
        return self.get_cached_list()

    def get_cached_list(self, overwrite: bool = None) -> list:
        """
        Used to automatically get a list of the set pymodel while following
        the set iteration limit and direction while caching the list for future list.

        Args:
            overwrite (bool, optional): Used to automatically overwrite a previously cached list.

        Returns:
             list: Instances of the set pymodel.
        """
        data = getattr(self, "_list", None)

        if data is None or overwrite:
            data = self._list = list(self)

        return data

    def crawl_data(self) -> None:
        """Used to get the next page's data and store it in _buffer."""
        self.shift_page_num()
        self.kwargs["params"]["page"] = self._page
        data = self.client.api(*self.args, **self.kwargs).json()
        if not data.get("data"):
            return

        # Store metadata
        self._page = data.pop("page")
        self.total_entries = data.pop("total_entries", None)
        self.total_pages = data.pop("total_pages", None)

        # Convert and store results.
        self._buffer.extend(self.pymodel.autoiter(data["data"], self.client))

    def get_starting_point(self) -> None:
        """Used to get the starting page number, making an api call if required."""
        if self.direction == Direction.UP:
            if self._page is None:
                self._page = 1

            self._page -= 1
        elif self.direction == Direction.DOWN:
            if self._page is None:
                data = self.client.api(*self.args, **self.kwargs).json()
                self._page = data.pop("total_pages")

            self._page += 1
        else:
            raise TypeError(f"Invalid pagination direction: {self.direction}")

    def reset(self, page: int = None) -> None:
        """
        Used to reset the iteration and delete any stored data.

        Args:
            page (int, optional): Used to specify the starting page.
        """
        self._page = page
        self.get_starting_point()
        self._buffer.clear()

    def shift_page_num(self) -> None:
        """Move the page number by one based on self.direction."""
        if self.direction == Direction.UP:
            self._page += 1
        elif self.direction == Direction.DOWN:
            self._page -= 1
        else:
            raise TypeError(f"Invalid pagination direction: {self.direction}")
