# Privacy.py
A Python wrapper for the [Privacy API](https://developer.privacy.com/).

## Installation
To install Privacy.py with pip, simply run this:
```
pip install Privacy.py
```

## Usage

The privacy api has 3 groups of endpoints: basic endpoints, premium endpoints and sandboxed endpoints. 

### Basic endpoints
These endpoints can be access by any account. 

```python
import privacy

client = privacy.Client("api-key")

# Returns an iterator of the cards available to your account (based on optional args).
iter_cards = client.cards_list(
    token=str,  # The token of a specific card (will still return an iterator of either 1 or 0 object(s)).
    begin="YYYY-MM-DD",  # Used to specify the date that the results should start on.
    end="YYYY-MM-DD",  # Used to specify the date that the results should end on.
)

# Returns an iterator of the transactions related to your account (based on optional args).
iter_transactions = client.transactions_list(
    approval_status="all",  # Used to only get transactions with a specific status.
                            # (can be `approvals`, `declines` or `all` and defaults to `all`
    token=str,  # Used to get a specific transaction (will still return an iterator if passed).
    card_token=str,  # Used to get the transactions related to a specific card.
    begin="YYYY-MM-DD",  # Used to specify the date that the results should start on.
    end="YYYY-MM-DD",  # Used to specify the date that the results should end on.
)
# With this being mirrored by the following function on the Card object.
iter_transactions = Card.get_transactions(*, **)  # This function's args mirror client.transactions_list
# But without card_token set to the token of the card that the function is being called from.
```

### Premium endpoints. 

These endpoints can only be accessed by premium accounts. 

```python
# Used to create a card.
card = client.cards_create(
    card_type=privacy.schema.CardTypes,  # The card type.
    memo=str,  # An optional card name.
    spend_limit=int,  # An optional spend limit in pennies.
    spend_limit_duration=privacy.schema.CardSpendLimitDurations,  # An optional arg used to specify how long this car'd spendlimit lasts.
)

# Used to modify a card based on it's token and optional args.
card = client.cards_modify(
    token=str,  # The token of the card being modified.
    state=privacy.schema.CardStates,  # The optional new state of the card (settings to CLOSED cannot be reversed).
    memo=str,  # The optional new name of the card.
    spend_limit=int,  # The optional new spend limit for the card (in pennies).
    spend_limit_duration=privacy.schema.CardSpendLimitDurations,  # The optional new spend limit duration.
)
# With this being mirrored by the follow function on the Card object.
card.update(*, **)  # This function's args mirror client.cards_modify without the ability to passthrough a token.

# Used to get a hosted card UI.
client.hoisted_card_ui_get(
    embed_request=privacy.schema.EmbedRequest,  # An embed request object.
)
```

### Sandboxed endponts

The endpoints can only be accessed on Privacy's seperate sandboxed api which can be enabled by passing through `debug=True` to `privacy.Client.__init__`. 

* Any changes made on these endpoints won't effect Privacy's actual service as these exist purely for debugging purposes.

* These endpoints can be accessed using `client.[auth_simulate, void_simulate, clearing_simulate, return_simulate]`.
