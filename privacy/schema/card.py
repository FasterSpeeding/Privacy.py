"""The card related models and enums."""
from enum import Enum
import typing


from privacy.schema.base import CustomBase
from privacy.schema.funding import Account


class Type(Enum):
    """An enum of the Card Type."""
    SINGLE_USE = "SINGLE_USE"
    MERCHANT_LOCKED = "MERCHANT_LOCKED"
    UNLOCKED = "UNLOCKED"
    PHYSICAL = "PHYSICAL"


class State(Enum):
    """An enum of the Card State."""
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"


class SpendLimitDuration(Enum):
    """An enum of the Card Spend Limit Durations."""
    TRANSACTION = "TRANSACTION"
    MONTHLY = "MONTHLY"
    ANNUALLY = "ANNUALLY"
    FOREVER = "FOREVER"


class Card(CustomBase):
    """
    The card model.

    Attributes:
        cvv (str, premium): The three digit cvv code on the card.
        funding (privacy.schema.funding.Account): The card's funding account.
        exp_month (str, premium): The expiry month of this card (format MM).
        exp_year (str, premium): The expiry year of this card (format YYYY).
        hostname (str): The hostname of the card's locked merchant (empty if not applicable).
        last_four (str): The last four digits of the card's number.
        memo (str): The name of the card.
        spend_limit (int): The limit for transaction authorisations with this card (in pennies).
        spend_limit_duration (privacy.schema.card.SpendLimitDuration): The spend limit duration.
        token (str): The unique identifier of this card.
        type (privacy.schema.card.Type): The card type.
    """
    cvv: typing.Optional[str]
    funding: Account
    exp_month: typing.Optional[str]
    exp_year: typing.Optional[str]
    hostname: str
    last_four: str
    memo: str
    pan: str
    spend_limit: int
    spend_limit_duration: SpendLimitDuration
    state: State
    token: str
    type: Type

    def update(
            self, state: State = None, memo: str = None,
            spend_limit: int = None,
            spend_limit_duration: SpendLimitDuration = None,
            api_key: str = None) -> None:
        """
        PREMIUM ENDPOINT - Modify an existing card.

        Args:
            state (privacy.schema.card.State, optional): The card state.
            memo (str, optional): The name for the card.
            spend_limit (int, optional): The card spend limit (in pennies).
            spend_limit_duration (privacy.schema.card.SpendLimitDuration, optional): Spend limit duration.
            api_key (str, optional): A key used for overriding authentication.

        Note:
            Setting state to `privacy.schema.card.State.CLOSED` is
            a final action that cannot be undone.

        Raises:
            APIException (privacy.http_client.APIException): On status code 5xx and certain 429s.
            TypeError: If api authentication key is unset.
        """
        card = self.client.cards_modify(
            self.token, state, memo, spend_limit,
            spend_limit_duration, api_key,
        )
        self.__init__(**card.dict())

    def get_transactions(
            self, approval_status: str = "all", token: str = None,
            page: int = None, page_size: int = None, begin: str = None,
            end: str = None, api_key: str = None):
        """
        Get an iterator of the transactions under this account.

        Args:
            approval_status (str, optional): One of [`approvals`, `declines`, `all`] used to
                get transactions with a specific status.
            token (str, optional): Used to get a specific transaction.
            page (int, optional): Used to specify the start page.
            page_size (int, optional): Used to specify the page size.
            begin (str, optional): The starting date of the results as a date string (`YYYY-MM-DD`).
            end (str, optional): The end date of the results as a date string (`YYYY-MM-DD`).
            api_key (str, optional): Used to override authentication.

        Returns:
            `privacy.util.pagination.PaginatedResponse`[ `privacy.schema.transaction.Transaction` ]

        Raises:
            APIException (privacy.http_client.APIException): On status code 5xx and certain 429s.
            TypeError: If api authentication key is unset.
        """
        return self.client.transactions_list(
            approval_status, token, self.token,
            page, page_size, begin, end, api_key)

    def __repr__(self):
        return f"<Card({self.memo}:{self.token})>"


__all__ = ["Type", "State", "SpendLimitDuration", "Card"]
