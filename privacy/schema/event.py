"""The transaction event related objects and enums."""
from datetime import datetime
from enum import Enum


from privacy.schema.base import CustomBase


class Result(Enum):
    """An enum of the transaction results."""
    APPROVED = "APPROVED"
    CARD_PAUSED = "CARD_PAUSED"
    CARD_CLOSED = "CARD_CLOSED"
    GLOBAL_TRANSACTION_LIMIT = "GLOBAL_TRANSACTION_LIMIT"
    GLOBAL_WEEKLY_LIMIT = "GLOBAL_WEEKLY_LIMIT"
    GLOBAL_MONTHLY_LIMIT = "GLOBAL_MONTHLY_LIMIT"
    USER_TRANSACTION_LIMIT = "USER_TRANSACTION_LIMIT"
    UNAUTHORIZED_MERCHANT = "UNAUTHORIZED_MERCHANT"
    SINGLE_USE_RECHARGED = "SINGLE_USE_RECHARGED"
    BANK_CONNECTION_ERROR = "BANK_CONNECTION_ERROR"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    MERCHANT_BLACKLIST = "MERCHANT_BLACKLIST"
    INVALID_CARD_DETAILS = "INVALID_CARD_DETAILS"
    BANK_NOT_VERIFIED = "BANK_NOT_VERIFIED"
    INACTIVE_ACCOUNT = "INACTIVE_ACCOUNT"
    UNKNOWN_HOST_TIMEOUT = "UNKNOWN_HOST_TIMEOUT"
    SWITCH_INOPERATIVE_ADVICE = "SWITCH_INOPERATIVE_ADVICE"
    FRAUD_ADVICE = "FRAUD_ADVICE"


class Type(Enum):
    """An enum of the event types"""
    AUTHORIZATION = "AUTHORIZATION"
    AUTHORIZATION_ADVICE = "AUTHORIZATION_ADVICE"
    CLEARING = "CLEARING"  # TODO: the docs are probably dodgy
    VOID = "VOID"  # apparently this is "CLEARING VOID"
    RETURN = "RETURN"


class Event(CustomBase):
    """
    The Event model.

    Attributes:
        amount (int): The amount of the transaction event (in pennies).
        created (datetime.datetime): The datetime of when this event was entered into the system.
        result (privacy.schema.event.Result): The transaction result.
        token (str): The globally unique identifier of the event.
        type (privacy.schema.event.Type): The event type.
    """
    amount: int
    created: datetime
    result: Result  # TODO: Check this
    token: str
    type: Type

    def __repr__(self):
        return f"<Event({self.token}:{self.type})>"


__all__ = ["Result", "Type", "Event"]
