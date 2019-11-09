"""The data models and enums returned and accepted by the api."""
from datetime import datetime
from enum import Enum
import typing

from pydantic import BaseModel

from privacy.util.functional import get_dict_path
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
            `privacy.util.pagination.PaginatedResponse`[ `privacy.schema.CustomBase` ]
        """
        return PaginatedResponse(cls, *args, **kwargs)

    @classmethod
    def autoiter(cls, data: list, client=None) -> typing.Generator:
        """
        Get a generator of instances of this object.

        Args:
            data (list): Dict objects that match this class to be converted.
            client (privacy.api_client.APIClient, optional): An APIClient used for allowing
                api calls from the returned object(s).

        Returns:
            generator: Subclasses of `privacy.schema.CustomBase`
        """
        for obj in data:
            yield cls(client=client, **obj)

    @classmethod
    def autodict(cls, data: list, path: list, client=None) -> dict:
        """
        Get a dict of instances of this object.

        Args:
            data (list): Dict objects that match this class to be converted.
            path (list): A path of string keys for getting the key used for each object.
            client (privacy.api_client.APIClient, optional): An APIClient used for allowing
                api calls from the returned object(s).

        Returns:
            dict: Subclasses of `privacy.schema.CustomBase`.
        """
        result = {}
        for obj in data:
            result[get_dict_path(obj, path)] = cls(client=client, **obj)

        return result


class FundingAccountTypes(Enum):
    """An enum of the Funding Account Types."""
    DEPOSITORY_CHECKING = "DEPOSITORY_CHECKING"
    DEPOSITORY_SAVINGS = "DEPOSITORY_SAVINGS"
    CARD_DEBIT = "CARD_DEBIT"


class FundingAccount(CustomBase):
    """
    The funding account model.

    Attributes:
        account_name (str): The account name of the source (can be digits of account number).
        token (str): The global unique identifier for the account.
        type (privacy.schema.FundingAccountTypes): The type of funding source.
    """
    account_name: str
    token: str
    type: FundingAccountTypes


class CardTypes(Enum):
    """An enum of the Card Types."""
    SINGLE_USE = "SINGLE_USE"
    MERCHANT_LOCKED = "MERCHANT_LOCKED"
    UNLOCKED = "UNLOCKED"
    PHYSICAL = "PHYSICAL"


class CardStates(Enum):
    """An enum of the Card States."""
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"


class CardSpendLimitDurations(Enum):
    """An enum of the Card Spend Limit Durations."""
    TRANSACTION = "TRANSACTION"
    MONTHLY = "MONTHLY"
    ANNUALLY = "ANNUALLY"
    FOREVER = "FOREVER"


class Card(CustomBase):
    """
    The card model.

    Attributes:
        cvv (str, optional): PREMIUM The three digit cvv code on the card.
        funding (privacy.schema.FundingAccount): The card's funding account.
        exp_month (str, optional): PREMIUM The expiry month of this card (format MM).
        exp_year (str, optional): PREMIUM The expiry year of this card (format YYYY).
        hostname (str): The hostname of the card's locked merchant (empty if not applicable).
        last_four (str): The last four digits of the card's number.
        memo (str): The name of the card.
        spend_limit (int): The limit for transaction authorisations with this card (in pennies).
        spend_limit_duration (privacy.schema.CardSpendLimitDurations): The spend limit duration.
        token (str): The unique identifier of this card.
        type (privacy.schema.CardTypes): The card type.
    """
    cvv: typing.Optional[str]
    funding: FundingAccount
    exp_month: typing.Optional[str]
    exp_year: typing.Optional[str]
    hostname: str  # TODO: empty if not applicable?
    last_four: str
    memo: str
    pan: str
    spend_limit: int
    spend_limit_duration: CardSpendLimitDurations
    state: CardStates
    token: str
    type: CardTypes

    def update(
            self, state: CardStates = None, memo: str = None,
            spend_limit: int = None,
            spend_limit_duration: CardSpendLimitDurations = None,
            api_key: str = None) -> None:
        """
        PREMIUM ENDPOINT - Modify an existing card.

        Args:
            state (privacy.schema.CardStates, optional): The card state.
            memo (str, optional): The name for the card.
            spend_limit (int, optional): The card spend limit (in pennies).
            spend_limit_duration (privacy.schema.CardSpendLimitDurations, optional): Spend limit duration.
            api_key (str, optional): A key used for overriding authentication.

        Note:
            Setting state to `privacy.schema.CardSpendLimitDurations`.CLOSED is
            a final action that cannot be undone.
        """
        card = self.client.cards_modify(
            self.token, state, memo, spend_limit,
            spend_limit_duration, api_key,
        )
        self.__init__(**card.json())

    def __repr__(self):
        return f"<Card({self.memo}:{self.token})>"


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


class TransactionStatuses(Enum):
    """An enum of the transaction statuses"""
    PENDING = "PENDING"
    VOIDED = "VOIDED"
    SETTLING = "SETTLING"
    SETTLED = "SETTLED"
    BOUNCED = "BOUNCED"


class TransactionResults(Enum):
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


class EventTypes(Enum):
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
        result (privacy.schema.TransactionResults): The transaction result.
        token (str): The globally unique identifier of the event.
        type (privacy.schema.EventTypes): The event type.
    """
    amount: int
    created: datetime  # TODO: convert to datetime object
    result: TransactionResults  # TODO: Check this
    token: str
    type: EventTypes

    def __repr__(self):
        return f"<Event({self.token}:{self.type})>"


class Transaction(CustomBase):
    """
    The Transaction Model

    Attributes:
        amount (int): The authorization  amount of the transaction (in pennies).
        card (privacy.schema.Card): The card tied to this transaction.
        created (datetime.datetime): The datetime of when this transaction first occurred.
        events (list[ privacy.schema.Event ]): PREMIUM the events that have modified this.
        funding (list[ privacy.schema.FundingAccount ]): All the founding sources..
        merchant (privacy.schema.Merchant): The merchant tied to this transation.
        result (privacy.schema.TransactionResults): The result of this transaction.
        settled_amount (int): The amount of that has been settled (in pennies) (may change).
        status (privacy.schema.TransactionStatuses): The status of this transaction.
        token (int): The globally unique identifier for this transaction.
    """
    amount: int
    card: Card
    created: datetime
    events: typing.List[Event]
    funding: typing.List[FundingAccount]
    merchant: Merchant
    result: TransactionResults
    settled_amount: int
    status: TransactionStatuses
    token: str

    def __repr__(self):
        return f"<Transaction({self.token}:{self.status})>"


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
    expiration: typing.Optional[datetime]  # ISO 8601

    def __repr__(self):
        return f"<EmbedRequest({self.token})>"
