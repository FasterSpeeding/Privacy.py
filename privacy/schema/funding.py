"""The funding related models and enums."""
from enum import Enum
import typing


from privacy.schema.base import CustomBase


class Type(Enum):
    """An enum of the Funding Account Type."""
    DEPOSITORY_CHECKING = "DEPOSITORY_CHECKING"
    DEPOSITORY_SAVINGS = "DEPOSITORY_SAVINGS"
    CARD_DEBIT = "CARD_DEBIT"


class Account(CustomBase):
    """
    The funding account model.

    Attributes:
        account_name (str): The account name of the source (can be digits of account number).
        token (str): The global unique identifier for the account.
        type (privacy.schema.funding.Type): The type of funding source.
    """
    account_name: typing.Optional[str]  # TODO: This is undocumented behaviour where unset in possible new obj.
    amount: typing.Optional[int]  # TODO: this is an undocumented attributed and may justify a new obj.
    token: str
    type: Type


__all__ = ["Type", "Account"]
