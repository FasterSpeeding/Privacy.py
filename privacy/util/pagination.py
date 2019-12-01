"""Used for handling paginated api endpoints."""
from enum import Enum
import typing


class Direction(Enum):
    """An enum of the directions used by `privacy.util.pagination.PaginatedResponse`"""
    UP = 0
    DOWN = 1


class PaginatedResponse:
    """
    Used for automatically iterating through paginated api endpoints.

    Attributes:
        args: Args passed through to `requests.session.request`.
        client (privacy.api_client.APIClient): The client used for api calls.
        direction (privacy.util.pagination.Direction): The direction for crawling through pages.
        kwargs: Kwargs passed through to `requests.session.request`.
        limit (int, optional): The amount of object(s) that this will return during iteration (unset for unlimited).
        metadata (dict, optional): Used to store extra data returned by the api (`total_entries` and `total_pages`).
        pymodel (privacy.schema.base.CustomBase): The dataclass this wraps and returns objects as during iteration.
    """
    direction: Direction = None
    limit: typing.Optional[int] = None
    metadata: dict = None
    _list: typing.Sequence = None
    _page: int = None

    def __init__(self, pymodel, client, *args, **kwargs: typing.Any) -> None:
        """
        Args:
            pymodel (privacy.schema.base.CustomBase): The dataclass that this will be
                returning objects as during iteration.
            client (privacy.api_client.APIClient): The api client used for making
                requests to crawl through pages.
            *args: Args passed through to `requests.session.request`.
            **kwargs: Kwargs passed through to `requests.session.request`.

        Raises:
            TypeError: If invalid pagination direction is supplied.
        """
        self.client = client
        self.pymodel = pymodel

        # Handle request args and kwargs
        if "params" in kwargs:
            self._page = kwargs["params"].pop("page", None)
        else:
            kwargs["params"] = {}
        self.args = args
        self.kwargs = kwargs

        self._buffer = []

    def __iter__(self) -> typing.Iterable:
        if self.direction is None:
            self.set_direction()

        return self

    def __next__(self) -> typing.Any:
        if self.limit:
            self.limit -= 1
        elif self.limit == 0:
            self.reset()
            raise StopIteration()

        if not self._buffer:
            self.crawl_data()

        try:
            return self._buffer.pop()
        except IndexError:
            self.reset()
            raise StopIteration()

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
        response = self.client.api(*self.args, **self.kwargs).json()
        data = response.pop("data", None)
        if not data:
            return

        # Store metadata
        self._page = response.pop("page")
        self.metadata = response

        # Convert and store results.
        self._buffer.extend(self.pymodel.autoiter(data, self.client))

    def get_starting_point(self) -> None:
        """Used to get the starting page number, making an api call if required."""
        if self.direction == Direction.UP:
            if self._page is None:
                self._page = 0
            elif self._page > 0:
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

    def set_direction(self, direction: Direction = Direction.UP, page: int = None) -> None:
        """
        Used to set the direction that this will crawl through pages during iteration.

        Args:
            direction (privacy.util.pagination.Direction, optional): The direction that this
                will crawl through pages, defaults to `privacy.util.pagination.Direction.UP`.
            page (int, optional): Used to set the page for this to start on during iteration.
        """
        self.direction = direction
        if page is not None:
            self._page = page

        self.get_starting_point()

    def shift_page_num(self) -> None:
        """Move the page number by one based on self.direction."""
        if self.direction == Direction.UP:
            self._page += 1
        elif self.direction == Direction.DOWN:
            self._page -= 1
        else:
            raise TypeError(f"Invalid pagination direction: {self.direction}")
