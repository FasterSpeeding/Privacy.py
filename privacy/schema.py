"""The data models and enums returned and accepted by the api."""
from datetime import datetime
from enum import Enum
import json
import typing

from pydantic import BaseModel

from privacy.util.functional import get_dict_path, JsonEncoder
from privacy.util.logging import LoggingClass
from privacy.util.pagination import PaginatedResponse


class UNSET:
    """Type used to represent optional attributes that aren't present."""
    @staticmethod
    def __nonzero__() -> bool:
        return False

    def __bool__(self) -> bool:
        return False


class CustomBase(BaseModel, LoggingClass):
    """A custom version of :class:`pydantic.BaseModel` used to handle api objects."""
    client: typing.Any = None
    _json_encoder = JsonEncoder

    def dict(self, **kwargs) -> dict:
        """Get this object's data as a dict."""
        data = super(CustomBase, self).dict(**kwargs)
        data.pop("client", None)
        return data

    def json(self, **kwargs) -> str:
        """Get this object's data as a stringified JSON."""
        data = {key: value for key, value in
                self.dict(**kwargs).items() if value is not UNSET}
        return json.dumps(data, cls=self._json_encoder)

    @classmethod
    def paginate(cls, *args, **kwargs) -> PaginatedResponse:
        """
        Get this class wrapped with PaginatedResponse.

        returns:
            :iterator:`privacy.util.pagination.PaginatedResponse`[
                :subclass:`privacy.schema.CustomBase`]
        """
        return PaginatedResponse(cls, *args, **kwargs)

    @classmethod
    def autoiter(cls, data: list, client=None) -> typing.Generator:
        """
        Get a generator of instances of this object.

        Args:
            data:
                A list of dict objects that match this class to be converted.
            client:
                An optional :class:`privacy.api_client.APIClient` used
                for allowing api calls from the returned object(s).

        Returns:
            A generator of :subclass:`privacy.schema.CustomBase`
        """
        for obj in data:
            yield cls(client=client, **obj)

    @classmethod
    def autodict(cls, data: list, path: list, client=None) -> dict:
        """
        Get a dict of instances of this object.

        Args:
            data:
                A list of dict objects that match this class to be converted.
            path:
                A list/path of string keys for getting the key used for each object.
            client:
                An optional :class:`privacy.api_client.APIClient` used
                for allowing api calls from the returned object(s).

        Returns:
            A dict[string] = :subclass:`privacy.schema.CustomBase`
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
        account_name:
            The string account name identifying the source (can be digits of account number).
        token:
            The string global unique identifier for the account.
        type:
            The type of funding source. :enum:`privacy.schema.FundingAccountTypes`
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
        cvv:
            PREMIUM: The string three digit cvv code on the card.
        funding:
            The card's funding account. :class:`privacy.schema.FundingAccount`
        exp_month
            PREMIUM: The string expiry month of this card (format MM).
        exp_year:
            PREMIUM: The string expiry year of this card (format YYYY).
        hostname:
            The hostname of the card's locked merchant (empty if not applicable).
        last_four:
            The string last four digits of the card's number.
        memo:
            The string name of the card.
        spend_limit:
            The int (in pennies) limit for transaction authorisations with this card.
        spend_limit_duration:
            :enum:`privacy.schema.CardSpendLimitDurations`
        token:
            The string unique identifier of this card.
        type:
            :enum:`privacy.schema.CardTypes`
    """
    cvv: str = UNSET
    funding: FundingAccount
    exp_month: str = UNSET
    exp_year: str = UNSET
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
            state:
                An optional :enum:`privacy.schema.CardStates`
            memo:
                An optional string name for the card.
            spend_limit:
                An optional int amount (pennies).
            spend_limit_duration:
                An optional :enum:`privacy.schema.spend_limit_duration`]
            api_key:
                An optional string used for overriding authentication.

        Note:
            Setting state to :enum:`privacy.schema.card_token`.CLOSED is
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
        acceptor_id:
            The string unique identify for this card acceptor.
        city:
            The string city of this card acceptor.
        country:
            The string country of this card acceptor.
        descriptor:
            The string description of this card acceptor.
        mcc:
            The string merchant category code.
        state:
            The string geographic state of this card acceptor.
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
        amount:
            The integer amount of the transaction event (pennies).
        created:
            :class:`datetime.datetime` of when this event was entered into the system.
        result:
            :enum:`privacy.schema.TransactionResults`
        token:
            The string globally unique identifier of the event.
        type:
            :enum:`privacy.schema.EventTypes`
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
        amount:
            The int authorization  amount (in pennies) of the transaction.
        card:
            :class:`privacy.schema.Card`
        created:
            :class:`datetime.datetime` of when this transaction first occured.
        events:
            PREMIUM - :class:`privacy.schema.Event`
        funding:
            List[:class:`privacy.schema.FundingAccount]
        merchant:
            :class:`privacy.schema.Merchant`
        result:
            :enum:`privacy.schema.TransactionResults`
        settled_amount:
            The int amount (in pennies) of the transaction that has been settled (may change).
        status:
            :class:`privacy.schema.TransactionStatuses`
        token:
            The int globally unique identifier for this transaction.
    """
    amount: int
    card: Card
    created: datetime
    events: typing.List[Event] = UNSET
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
        token:
            The globally unique identifier for the card to be displayed.
        css:
            A publicly available URI used for styling the hosted white-labeled iframe.
        expiration:
            OPTIONAL - The datetime for when the request should expire.
    """
    token: str
    css: str
    expiration: datetime = UNSET  # ISO 8601

    def __repr__(self):
        return f"<EmbedRequest({self.token})>"
