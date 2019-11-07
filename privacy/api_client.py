"""The main client of this module."""
from typing import Iterable


from privacy.http_client import HTTPClient, Routes
from privacy.schema import (
    Card, Transaction, CardSpendLimitDurations,
    CardStates, CardTypes, EmbedRequest,
)
from privacy.util.functional import b64_encode, hmac_sign, optional
from privacy.util.logging import LoggingClass
from privacy.util.pagination import Direction


def auth_header(api_key=None):
    """Optionally overwrite authorisation header for a single request."""
    return optional(Authorization=api_key)


class APIClient(LoggingClass):
    """
    The client used for using Privacy.com's restful api endpoints.

    Attributes:
        api:
            :class:`privacy.http_client.HTTPClient`
        api_key:
            The string key used for authentication and some functions.
            Will be mirrored with api.session.headers["Authorization"] when using update_api_key.
    """
    def __init__(
            self, api_key: str = None,
            backoff: bool = True, debug: bool = False) -> None:
        """
        Args:
            api_key:
                An optional string used for authentication.
            debug:
                An optional bool used for toggling the debug api.
            backoff:
                An optional bool used for disabling automatic
                backoff and retry on status codes 5xx or 429.
                Raises :class:`privacy.http_client.APIException` if False.
        """
        self.api = HTTPClient(api_key=api_key, backoff=backoff, debug=debug)
        self.api_key = api_key

    def update_api_key(self, api_key: str = None) -> None:
        """
        Update or unset the default authorisation key used by an initiated client.

        Args:
            api_key:
                An optional string used for authentication,
                will unset if not passed.
        """
        self.api_key = api_key
        if api_key:
            self.api.session.headers["Authorization"] = "api-key " + api_key
        else:
            self.api.session.headers.pop("Authorization", None)

    def cards_list(
            self, token: str = None, page: int = None, page_size: int = None,
            begin: str = None, end: str = None, direction: Direction = None,
            limit: int = None, api_key: str = None) -> Iterable[Card]:
        """
        Get an iterator of the cards owned by this account.

        Args:
            token:
                An optional string used to get a specific card.
            page:
                An optional int used for specifying the start page.
            page_size:
                An optional int used for specifying the page size.
            begin:
                An optional date string (in the format `YYYY-MM-DD`)
                used to specify the starting date for the results.
            end:
                An optional Date string (in the format `YYYY-MM-DD`)
                used to specify the end date for the results.
            direction:
                An optional :enum:`privacy.util.pagination.Direction`
                used for specifying the direction of the page iteration.
            limit:
                An optional int used to limit how many objects
                the returned iterator will return during iteration.
            api_key:
                An optional string used for overriding authentication.

        Returns:
            :iterator:`privacy.util.pagination.PaginatedResponse`[:class:`privacy.schema.Card`]
        """
        return Card.paginate(
            self,
            Routes.CARDS_LIST,
            headers=auth_header(api_key),
            direction=direction,
            limit=limit,
            params=optional(
                card_token=token,
                page=page,
                page_size=page_size,
                begin=begin,
                end=end,
            )
        )

    def transactions_list(
            self, approval_status: str = "all", token: str = None,
            page: int = None, page_size: int = None, begin: str = None,
            end: str = None, direction: Direction = None, limit: int = None,
            api_key: str = None) -> Iterable[Transaction]:
        """
        Get an iterator of the transactions under this account.

        Args:
            approval_status:
                An optional string [`approvals`, `declines`, `all`]
                used for returning transactions with a specific status.
            token:
                An optional string used to get a specific card.
            page:
                An optional int used for specifying the start page.
            page_size:
                An optional int used for specifying the page size.
            begin:
                An optional date string (in the format `YYYY-MM-DD`)
                used to specify the starting date for the results.
            end:
                An optional Date string (in the format `YYYY-MM-DD`)
                used to specify the end date for the results.
            direction:
                An optional :enum:`privacy.util.pagination.Direction`
                used for specifying the direction of the page iteration.
            limit:
                An optional int used to limit how many objects
                the returned iterator will return during iteration.
            api_key:
                An optional string used for overriding authentication.

        Returns:
            :iterator:`privacy.util.pagination.PaginatedResponse`[
                :class:`privacy.schema.Transaction`]
        """
        return Transaction.paginate(
            self,
            Routes.TRANSACTIONS_LIST,
            dict(approval_status=approval_status),
            headers=auth_header(api_key),
            direction=direction,
            limit=limit,
            params=optional(
                transaction_token=token,
                page=page,
                page_size=page_size,
                begin=begin,
                end=end,
            )
        )

    # Premium
    def cards_create(
            self, card_type: CardTypes, memo: str = None,
            spend_limit: int = None,
            spend_limit_duration: CardSpendLimitDurations = None,
            api_key=None) -> Card:
        """
        PREMIUM ENDPOINT - Create a card.

        Args:
            card_type:
                :enum:`privacy.schema.CardTypes`
            memo:
                An optional string name for the card.
            spend_limit:
                An optional int amount (pennies).
            spend_limit_duration:
                An optional :enum:`privacy.schema.spend_limit_duration`].
            api_key:
                An optional string used for overriding authentication.

        Returns:
            :class:`privacy.schema.Card`
        """
        request = self.api(
            Routes.CARDS_CREATE,
            headers=auth_header(api_key),
            json=optional(
                type=card_type,
                memo=memo,
                spend_limit=spend_limit,
                spend_limit_duration=spend_limit_duration,
            )
        )
        return Card(client=self.api, **request.json())

    def cards_modify(
            self, card_token: str, state: CardStates = None,
            memo: str = None, spend_limit: int = None,
            spend_limit_duration: CardSpendLimitDurations = None,
            api_key: str = None) -> Card:
        """
        PREMIUM ENDPOINT - Modify an existing card.

        Args:
            card_token:
                The unique token of the card to modify.
            state:
                An optional :enum:`privacy.schema.CardStates`.
            memo:
                An optional string name for the card.
            spend_limit:
                An optional int amount (pennies).
            spend_limit_duration:
                An optional :enum:`privacy.schema.spend_limit_duration`].
            api_key:
                An optional string used for overriding authentication.

        Returns:
            :class:`privacy.schema.Card`

        Note:
            Setting state to :enum:`privacy.schema.card_token`.CLOSED is
            a final action that cannot be undone.
        """
        request = self.api(
            Routes.CARDS_MODIFY,
            headers=auth_header(api_key),
            json=optional(
                card_token=card_token,
                state=state,
                memo=memo,
                spend_limit=spend_limit,
                spend_limit_duration=spend_limit_duration,
            )
        )
        return Card(client=self.api, **request.json())

    def hoisted_card_ui_get(
            self, embed_request: EmbedRequest, api_key: str = None) -> str:
        """
        PREMIUM ENDPOINT - get a hosted card UI

        Args:
            embed_request:
                :class:`privacy.schema.EmbedRequest`
            api_key:
                An optional string used for overriding authentication.

        Returns:
            A string iframe body.
        """
        embed_request_json = embed_request.json()
        embed_request = b64_encode(bytes(embed_request_json, "utf-8"))
        embed_request_hmac = hmac_sign(api_key or self.api_key, embed_request)

        return self.api(
            Routes.HOSTED_CARD_UI_GET,
            headers=auth_header(api_key),
            json=dict(embed_request=embed_request, hmac=embed_request_hmac),
        ).content

    # Sandbox
    def auth_simulate(
            self, descriptor: str, pan: str,
            amount: int, api_key: str = None) -> dict:
        """
        SANDBOX ENDPOINT - Simulate an auth request from a merchant acquirer.

        Args:
            descriptor:
                A string merchant's descriptor.
            pan:
                A string 16 digit card number.
            amount:
                An int amount (pennies) to authorise.
            api_key:
                An optional string used for overriding authentication.

        Returns:
            {"token": str}
        """
        return self.api(
            Routes.SIMULATE_AUTH,
            headers=auth_header(api_key),
            json=dict(
                descriptor=descriptor,
                pan=pan,
                amount=amount,
            )
        ).json()

    def void_simulate(
            self, token: str, amount: int, api_key: str = None):
        """
        SANDBOX ENDPOINT - Void an existing, uncleared/pending authorisation.

        Args:
            token:
                The string transaction token returned by Routes.SIMULATE_AUTH.
            amount:
                The int amount (pennies) to void.
                Can be less than or equal to original authorisation.
            api_key:
                An optional string used for overriding authentication.
        """
        self.api(
            Routes.SIMULATE_VOID,
            headers=auth_header(api_key),
            json=dict(token=token, amount=amount),
        )

    def clearing_simulate(
            self, token: str, amount: int, api_key: str = None):
        """
        SANDBOX ENDPOINT - Clear an existing authorisation.

        Args:
            token:
                The string transaction token returned by Routes.SIMULATE_AUTH.
            amount:
                The int amount (pennies) to complete.
                Can be less than or equal to original authorisation.
            api_key:
                An optional string used for overriding authentication.
        """
        self.api(
            Routes.SIMULATE_CLEARING,
            headers=auth_header(api_key),
            json=dict(token=token, amount=amount),
        )

    def return_simulate(
            self, descriptor: str, pan: str,
            amount: int, api_key: str = None) -> dict:
        """
        SANDBOX ENDPOINT - Return/refund an amount back to a card.

        Args:
            descriptor:
                A string merchant's descriptor.
            pan:
                A string 16 digit card number.
            amount:
                The int amount (pennies) to return to the card.
                Can be less than or equal to original authorisation.
            api_key:
                An optional string used for overriding authentication.

        Returns:
            {"token": str}
        """
        return self.api(
            Routes.SIMULATE_RETURN,
            headers=auth_header(api_key),
            json=dict(
                descriptor=descriptor,
                pan=pan,
                amount=amount,
            )
        ).json()
