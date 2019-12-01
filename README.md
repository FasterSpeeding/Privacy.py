# Privacy.py
A Python wrapper for the [Privacy API](https://developer.privacy.com/).

## Installation

To install Privacy.py into your environment, simply run this:

```
pip install Privacy.py
```

## Usage

Privacy's api has 3 groups of endpoints (which are differentiated by access):
basic endpoints, premium endpoints and sandboxed endpoints. 

### Basic endpoints

These endpoints can be access by any account. 

```python
import privacy

client = privacy.Client("api-key")  # This supports `with privacy.Client("api-key") as client:`

# Returns an iterator of the cards available to your account (based on optional args).
iter_cards = client.cards_list(
    token=str,  # The token of a specific card (will still return an iterator of either 1 or 0 object(s)).
    begin="YYYY-MM-DD",  # Used to get cards that were created after the specified date.
    end="YYYY-MM-DD",  # Used to get cards that were created before the specified date.
)

# Returns an iterator of the transactions related to your account (based on optional args).
iter_transactions = client.transactions_list(
    approval_status="all",  # Used to only get transactions with a specific status.
                            # Can be `approvals`, `declines` or `all` and defaults to `all`.
    token=str,  # Used to get a specific transaction (will still return an iterator if passed).
    card_token=str,  # Used to get transactions related to a specific card.
    begin="YYYY-MM-DD",   # Used to get transactions that were created after the specified date.
    end="YYYY-MM-DD",  # Used to get transactions that were created before the specified date.
)
# With this being mirrored by the following function on the Card object.
iter_transactions = Card.get_transactions(*, **)  # Where card_token is from card this is attached to.
```

### Premium endpoints. 

These endpoints can only be accessed by premium accounts. 

```python
# Used to create a card.
card = client.cards_create(
    card_type=privacy.schema.card.Type,  # The card type.
    memo=str,  # An optional card name.
    spend_limit=int,  # An optional spend limit (in pennies).
    spend_limit_duration=privacy.schema.card.SpendLimitDuration,  # Optional, used to set how long the spend limit lasts.
)

# Used to modify a card based on it's token and optional args.
card = client.cards_modify(
    token=str,  # The token of the card being modified.
    state=privacy.schema.CardStates,  # Used to change the state of the card (cannot be reversed when set to `CLOSED`).
    memo=str,  # Used to change the name of the card.
    spend_limit=int,  # Used to change spend limit for the card (in pennies).
    spend_limit_duration=privacy.schema.card.SpendLimitDuration,  # Used to change how long the spend limit lasts.
)
# With this being mirrored by the following function on the Card object.
card.update(*, **)  # Where the token used is from the card this is attached to.

# Used to get a hosted card UI.
client.hoisted_card_ui_get(
    embed_request=privacy.schema.embed.EmbedRequest,  # An embed request object.
)
```

### Sandboxed endponts

The endpoints can only be accessed on Privacy's separate sandboxed api
(switched to by passing `sandboxed=True` through to `privacy.Client.__init__`).

* Any changes made on these endpoints won't effect Privacy's actual service as these exist purely for debugging purposes.

* These endpoints can be accessed using `client.[auth_simulate, void_simulate, clearing_simulate, return_simulate]`.
