from privacy.util.json import CustomJsonEncoder
from privacy.schema import funding


def test_CustomJsonEncoder():
    json_string = CustomJsonEncoder.dumps(
        {
            "account": funding.Account(
                amount=40, name="ok", token="43942", type=funding.Type.CARD_DEBIT
            ),
        }
    )
    assert (
        json_string
        == '{"account": "{\\"account_name\\": null, \\"amount\\": 40, '
           '\\"token\\": \\"43942\\", \\"type\\": \\"CARD_DEBIT\\"}"}'
    )
