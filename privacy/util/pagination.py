from enum import Enum
from typing import Any, Iterable, Union


class Direction(Enum):
    UP = 0
    DOWN = 1


class PaginatedResponse:
    total_entries = None
    total_pages = None
    _list = None

    def __init__(
            self, pymodel, client: Union[object, None],
            *args, direction: Direction = None,
            limit: int = None, **kwargs: Any) -> None:
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
        return self.get_cached_list()

    def get_cached_list(self, overwrite: bool = None) -> list:
        data = getattr(self, "_list", None)

        if data is None or overwrite:
            data = self._list = list(self)

        return data

    def crawl_data(self) -> None:
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
        self._page = page
        self.get_starting_point()
        self._buffer.clear()

    def shift_page_num(self) -> None:
        if self.direction == Direction.UP:
            self._page += 1
        elif self.direction == Direction.DOWN:
            self._page -= 1
        else:
            raise TypeError(f"Invalid pagination direction: {self.direction}")
