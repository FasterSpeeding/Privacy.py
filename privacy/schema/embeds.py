"""The embed related model(s)."""
from datetime import datetime
import typing


from privacy.schema.base import CustomBase


class EmbedRequest(CustomBase):
    """
    The EmbedRequest model.

    Attributes:
        token (str): The globally unique identifier for the card to be displayed.
        css (str): A publicly available URI used for styling the hosted white-labeled iframe.
        expiration (datetime.datetime, optional): The datetime for when the request should expire.
    """
    token: str
    css: str
    expiration: typing.Optional[datetime]

    def __repr__(self):
        return f"<EmbedRequest({self.token})>"


__all__ = ["EmbedRequest"]
