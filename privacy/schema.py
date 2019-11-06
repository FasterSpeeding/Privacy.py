from datetime import datetime
from enum import Enum
import json
import typing

from pydantic import BaseModel

from privacy.util.functional import get_dict_path, JsonEncoder
from privacy.util.logging import LoggingClass
from privacy.util.pagination import PaginatedResponse


class UNSET:
    @staticmethod
    def __nonzero__() -> bool:
        return False

    def __bool__(self) -> bool:
        return False


class CustomBase(BaseModel, LoggingClass):
    client: typing.Any = None
    _json_encoder = JsonEncoder

    def dict(self, **kwargs) -> dict:
        """Get this object's data in a dict."""
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
                An optional :class:`privacy.http_client.HTTPClient` used
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
                An optional :class:`privacy.http_client.HTTPClient` used
                for allowing api calls from the returned object(s).

        Returns:
            A dict[string] = :subclass:`privacy.schema.CustomBase`
        """
        result = {}
        for obj in data:
            result[get_dict_path(obj, path)] = cls(client=client, **obj)

        return result


class FundingAccountTypes(Enum):
    DEPOSITORY_CHECKING = "DEPOSITORY_CHECKING"
    DEPOSITORY_SAVINGS = "DEPOSITORY_SAVINGS"
    CARD_DEBIT = "CARD_DEBIT"


class FundingAccount(CustomBase):
    account_name: str
    token: str
    type: FundingAccountTypes


class CardTypes(Enum):
    SINGLE_USE = "SINGLE_USE"
    MERCHANT_LOCKED = "MERCHANT_LOCKED"
    UNLOCKED = "UNLOCKED"
    PHYSICAL = "PHYSICAL"


class CardStates(Enum):
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"


class CardSpendLimitDurations(Enum):
    TRANSACTION = "TRANSACTION"
    MONTHLY = "MONTHLY"
    ANNUALLY = "ANNUALLY"
    FOREVER = "FOREVER"


class Card(CustomBase):
    cvv: str = UNSET
    funding: FundingAccount
    exp_month: str = UNSET
    exp_year: str = UNSET
    hostname: str
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
        return self.client.cards_modify(
            self.token, state, memo, spend_limit,
            spend_limit_duration, api_key
        )

    def __repr__(self):
        return f"<Card({self.memo}:{self.token})>"


class Merchant(CustomBase):
    acceptor_id: str
    city: str
    country: str
    descriptor: str
    mcc: str
    state: str

    def __repr__(self):
        return f"<Merchant({self.acceptor_id})>"


class TransactionStatuses(Enum):
    PENDING = "PENDING"
    VOIDED = "VOIDED"
    SETTLING = "SETTLING"
    SETTLED = "SETTLED"
    BOUNCED = "BOUNCED"


class TransactionResults(Enum):
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
    AUTHORIZATION = "AUTHORIZATION"
    AUTHORIZATION_ADVICE = "AUTHORIZATION_ADVICE"
    CLEARING = "CLEARING"  # TODO: the docs are probably dodgy
    VOID = "VOID"  # apparently this is "CLEARING VOID"
    RETURN = "RETURN"


class Event(CustomBase):
    amount: int
    created: datetime  # TODO: convert to datetime object
    result: TransactionResults  # TODO: Check this
    token: str
    type: EventTypes

    def __repr__(self):
        return f"<Event({self.token}:{self.type})>"


class Transaction(CustomBase):
    amount: int
    card: Card
    created: datetime
    events: typing.List[Event] = UNSET
    funding: FundingAccount
    merchant: Merchant
    result: TransactionResults
    settled_amount: int
    status: TransactionStatuses
    token: str

    def __repr__(self):
        return f"<Transaction({self.token}:{self.status})>"


class EmbedRequest(CustomBase):
    token: str
    css: str
    expiration: datetime  # ISO 8601

    def __repr__(self):
        return f"<EmbedRequest({self.token})>"
