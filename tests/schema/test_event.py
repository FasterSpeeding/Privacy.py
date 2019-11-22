"""Tests for Privacy.schema.event"""
from privacy.schema import event


def test_event():
    event_obj = event.Event(**{
        "amount": "50",
        "created": "1574366333",
        "result": "BANK_CONNECTION_ERROR",
        "token": "3495-3234-5439-2342",
        "type": "VOID"
    })
    assert event_obj.amount == 50
    assert event_obj.created.isoformat() == "2019-11-21T19:58:53+00:00"
    assert event_obj.result is event.Result.BANK_CONNECTION_ERROR
    assert event_obj.token == "3495-3234-5439-2342"
    assert event_obj.type is event.Type.VOID
