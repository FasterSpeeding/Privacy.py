"""Used for handling paginated api endpoints."""
from enum import Enum
from typing import Any, Iterable


class Direction(Enum):
    """
    An enum of the directions used by
    :class:`privacy.util.pagination.PaginatedResponse`
    """
    UP = 0
    DOWN = 1


class PaginatedResponse:
    """Used for automatically iterating through paginated api endpoints."""
    total_entries = None
    total_pages = None
    _list = None

    def __init__(
            self, pymodel, client,
            *args, direction: Direction = None,
            limit: int = None, **kwargs: Any) -> None:
        """
        Args:
            pymodel:
                A :subclass:`privacy.schema.CustomBase` dataclass
                that this will be returning objects as during iteration.
            client:
                :class:`privacy.http_client.APIClient` used
                for making requests to crawl through pages.
            args:
                Args passed through to :class:`requests.session.request`.
            direction:
                An optional :enum:`privacy.util.pagination.Direction`
                used for specifying the direction of the page iteration.
            limit:
                An optional int used to limit how many objects
                this will return while being iterated through.
            kwargs:
                Kwargs passed through to :class:`requests.session.request`.
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
        the set iteration limit and direction, and caching the list for future list.

        Args:
            overwrite:
                An optional bool used to automatically overwrite any previously cached lists.

        Returns:
             A list of instances of the set pymodel.
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
            page:
                An optional int used to specify the starting page.
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
