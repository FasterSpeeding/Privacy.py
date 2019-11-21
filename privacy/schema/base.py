"""The base object used for forming api models."""
from datetime import datetime
from enum import Enum
import typing


from pydantic import BaseModel


from privacy.util.functional import get_attr_path
from privacy.util.logging import LoggingClass
from privacy.util.pagination import PaginatedResponse


class CustomBase(BaseModel, LoggingClass):
    """A custom version of `pydantic.BaseModel` used to handle api objects."""
    client: typing.Any = None

    class Config:
        """Config for customising the behaviour of CustomBase."""
        json_encoders = {
            datetime: lambda obj: obj.isoformat(),
            Enum: lambda obj: obj.value,
        }

    def dict(self, *args, **kwargs) -> dict:
        """Get this object's data as a dict."""
        data = super(CustomBase, self).dict(*args, **kwargs)
        data.pop("client", None)
        return data

    @classmethod
    def paginate(cls, *args, **kwargs) -> PaginatedResponse:
        """
        Get this class wrapped with PaginatedResponse.

        Returns:
            `privacy.util.pagination.PaginatedResponse`[ `privacy.schema.base.CustomBase` ]
        """
        return PaginatedResponse(cls, *args, **kwargs)

    @classmethod
    def autoiter(cls, data: list, client=None) -> typing.Iterable:
        """
        Get a generator of instances of this object.

        Args:
            data (list): Dict objects that match this class to be converted.
            client (privacy.api_client.APIClient, optional): An APIClient used for allowing
                api calls from the returned object(s).

        Returns:
            generator: Subclasses of `privacy.schema.base.CustomBase`
        """
        return map(lambda obj: cls(client=client, **obj), data)

    @classmethod
    def autodict(cls, data: list, path: list, client=None) -> dict:
        """
        Get a dict of instances of this object.

        Args:
            data (list): Dict objects that match this class to be converted.
            path (list): A path of string attributes for getting the key used for each object.
            client (privacy.api_client.APIClient, optional): An APIClient used for allowing
                api calls from the returned object(s).

        Returns:
            dict: Subclasses of `privacy.schema.base.CustomBase`.
        """
        result = {}
        for dict_obj in data:
            obj = cls(client=client, **dict_obj)
            result[get_attr_path(obj, path)] = obj

        return result
