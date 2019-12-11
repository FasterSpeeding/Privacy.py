"""The transaction related models and enums."""
from datetime import datetime
from enum import Enum
import typing


from privacy.schema.base import CustomBase
from privacy.schema.cards import Card
from privacy.schema.events import Event, Result
from privacy.schema.fundings import Account
from privacy.schema.merchants import Merchant


class Status(Enum):
    """An enum of the transaction statuses"""

    PENDING = "PENDING"
    VOIDED = "VOIDED"
    SETTLING = "SETTLING"
    SETTLED = "SETTLED"
    BOUNCED = "BOUNCED"


class Transaction(CustomBase):
    """
    The Transaction Model

    Attributes:
        amount (int): The authorization  amount of the transaction (in pennies).
        card (privacy.schema.cards.Card): The card tied to this transaction.
        created (datetime.datetime): The datetime of when this transaction first occurred.
        events (tuple[ privacy.schema.events.Event ], premium): the events that have modified this.
        funding (tuple[ privacy.schema.fundings.Account ]): All the founding sources.
        merchant (privacy.schema.merchants.Merchant): The merchant tied to this transaction.
        result (privacy.schema.events.Result): The result of this transaction.
        settled_amount (int): The amount of that has been settled (in pennies) (may change).
        status (privacy.schema.transactions.Status): The status of this transaction.
        token (int): The globally unique identifier for this transaction.
    """

    amount: int
    card: Card
    created: datetime
    events: typing.Tuple[Event]
    funding: typing.Tuple[Account]
    merchant: Merchant
    result: Result
    settled_amount: int
    status: Status
    token: str

    def __repr__(self):
        return f"<Transaction({self.token}:{self.status})>"


__all__ = ["Status", "Transaction"]
