"""The merchant model."""
from privacy.schema.base import CustomBase


class Merchant(CustomBase):
    """
    The Merchant model.

    Attributes:
        acceptor_id (str): The unique identify for this card acceptor.
        city (str): The city of this card acceptor.
        country (str): The country of this card acceptor.
        descriptor (str): The description of this card acceptor.
        mcc (str): The merchant category code.
        state (str): The geographic state of this card acceptor.
    """
    acceptor_id: str
    city: str
    country: str
    descriptor: str
    mcc: str
    state: str

    def __repr__(self):
        return f"<Merchant({self.acceptor_id})>"


__all__ = ["Merchant"]
