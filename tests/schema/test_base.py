"""Tests for privacy.schema.base"""
from datetime import datetime
import typing


import pytest


from privacy.schema import base
from privacy.util import pagination


@pytest.fixture
def mock_payload():
    return {"testing": "hi there", "i_int": "55", "date": "1574366333"}


@pytest.fixture()
def MockModel(mock_payload):
    class MockModel(base.CustomBase):
        testing: str
        i_int: int
        date: datetime
        optional: typing.Optional[str]

    return MockModel(**mock_payload)


@pytest.mark.model
class TestModel:
    @staticmethod
    def test_model(MockModel):
        assert MockModel.testing == "hi there"
        assert MockModel.i_int == 55
        assert MockModel.date.isoformat() == "2019-11-21T19:58:53+00:00"
        assert MockModel.optional is None

    @staticmethod
    def test_model_dict(MockModel):
        assert MockModel.dict() == {
            "testing": "hi there",
            "i_int": 55,
            "date": datetime.fromisoformat("2019-11-21T19:58:53+00:00"),
            "optional": None,
        }

    @staticmethod
    def test_model_json(MockModel):
        assert (
            MockModel.json()
            == '{"testing": "hi there", "i_int": 55, "date": "2019-11-21T19:58:53+00:00", "optional": null}'
        )

    @staticmethod
    def test_paginate(MockModel):
        mock_paginated_model = MockModel.paginate(None)
        assert isinstance(mock_paginated_model, pagination.PaginatedResponse)
        assert isinstance(MockModel, mock_paginated_model.pymodel)

    @staticmethod
    def test_autoiter(MockModel, mock_payload):
        mock_iter = MockModel.autoiter([mock_payload])
        assert list(mock_iter)[0] == MockModel

    @staticmethod
    def test_autodict(MockModel, mock_payload):
        mock_dict = MockModel.autodict([mock_payload], ("i_int", ))
        assert mock_dict[55] == MockModel
