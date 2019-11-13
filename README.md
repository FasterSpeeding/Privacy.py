# Privacy.py
A Python wrapper for the [Privacy API](https://developer.privacy.com/).

## Installation
To install Privacy.py with pip, simply run this:
```
pip install Privacy.py
```

## Basic usage

```python
import privacy

client = privacy.Client("api-key")

# Returns an iterator of the cards available to your account (based on optional args).
iter_cards = client.cards_list(
    token="TOKEN",  # The token of a specific card (will still return an iterator of either 1 or 0 object(s)).
    begin="YYYY-MM-DD",  # Used to specify the date that the results should start on.
    end="YYYY-MM-DD",  # Used to specify the date that the results should end on.
)

# Returns an iterator of the transactions related to your account (based on optional args).
iter_transactions = client.transactions_list(
    approval_status="all",  # Used to only get transactions with a specific status.
                            # (can be `approvals`, `declines` or `all` and defaults to `all`
    token="TRANSACTION_TOKEN",  # Used to get a specific transaction (will still return an iterator if passed).
    card_token="CARD_TOKEN",  # Used to get the transactions related to a specific card.
    begin="YYYY-MM-DD",  # Used to specify the date that the results should start on.
    end="YYYY-MM-DD",  # Used to specify the date that the results should end on.
)
# With this being mirrored by the following function on the Card object.
iter_transactions = Card.get_transactions(*, **)  # This function's args mirror client.transactions_list
# But without card_token set to the token of the card that the function is being called from.

# The following api endpoints are only available to premium accounts.

# Used to create a card.
card = client.cards_create(
    card_type=privacy.schema.CardTypes,  # The card type.
    memo="I am a card name",  # An optional card name.
    spend_limit=500,  # An optional spend limit in pennies.
    spend_limit_duration=privacy.schema.CardSpendLimitDurations,  # An optional arg used to specify how long this car'd spendlimit lasts.
)

# Used to modify a card based on it's token and optional args.
card = client.cards_modify(
    token="TOKEN",  # The token of the card being modified.
    state=privacy.schema.CardStates,  # The optional new state of the card (settings to CLOSED cannot be reversed).
    memo="I am a card.",  # The optional new name of the card.
    spend_limit=500,  # The optional new spend limit for the card (in pennies).
    spend_limit_duration=privacy.schema.CardSpendLimitDurations,  # The optional new spend limit duration.
)
# With this being mirrored by the follow function on the Card object.
card.update(*, **)  # This function's args mirror client.cards_modify without the ability to passthrough a token.

# Used to get a hosted card UI.
client.hoisted_card_ui_get(
    embed_request=privacy.schema.EmbedRequest,  # An embed request object.
)
```
