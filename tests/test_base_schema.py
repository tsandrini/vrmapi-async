"""Tests for generic base response models."""

import pytest
from pydantic import ValidationError

from vrmapi_async.client.base.schema import (
    BaseModel,
    PaginatedRecordsResponse,
    RecordsListResponse,
    RecordsSingleResponse,
)


class SampleItem(BaseModel):
    """Simple model for testing generic response containers."""

    name: str
    value: int


# ---------------------------------------------------------------------------
# RecordsListResponse
# ---------------------------------------------------------------------------


class TestRecordsListResponse:
    def test_parses_list_of_models(self):
        data = {
            "success": True,
            "records": [
                {"name": "a", "value": 1},
                {"name": "b", "value": 2},
            ],
        }
        resp = RecordsListResponse[SampleItem](**data)
        assert resp.success is True
        assert len(resp.records) == 2
        assert isinstance(resp.records[0], SampleItem)
        assert resp.records[0].name == "a"
        assert resp.records[1].value == 2

    def test_empty_records_default(self):
        data = {"success": True}
        resp = RecordsListResponse[SampleItem](**data)
        assert resp.records == []

    def test_raw_preserved(self):
        data = {
            "success": True,
            "records": [{"name": "x", "value": 0}],
        }
        resp = RecordsListResponse[SampleItem](**data)
        assert resp._raw == data

    def test_subclass_inherits_behavior(self):
        class MySitesResponse(RecordsListResponse[SampleItem]):
            """Concrete subclass."""

        data = {"success": True, "records": [{"name": "s", "value": 3}]}
        resp = MySitesResponse(**data)
        assert isinstance(resp, RecordsListResponse)
        assert resp.records[0].name == "s"
        assert resp._raw == data


# ---------------------------------------------------------------------------
# RecordsSingleResponse
# ---------------------------------------------------------------------------


class TestRecordsSingleResponse:
    def test_parses_single_model(self):
        data = {"success": True, "records": {"name": "only", "value": 42}}
        resp = RecordsSingleResponse[SampleItem](**data)
        assert resp.success is True
        assert isinstance(resp.records, SampleItem)
        assert resp.records.name == "only"
        assert resp.records.value == 42

    def test_raw_preserved(self):
        data = {"success": True, "records": {"name": "r", "value": 0}}
        resp = RecordsSingleResponse[SampleItem](**data)
        assert resp._raw == data

    def test_subclass_with_extra_fields(self):
        class StatsResponse(RecordsSingleResponse[SampleItem]):
            """Subclass adding extra fields beyond records."""

            totals: dict[str, int]

        data = {
            "success": True,
            "records": {"name": "stat", "value": 10},
            "totals": {"sum": 100},
        }
        resp = StatsResponse(**data)
        assert resp.records.name == "stat"
        assert resp.totals == {"sum": 100}

    def test_missing_records_raises(self):
        with pytest.raises(ValidationError):
            RecordsSingleResponse[SampleItem](success=True)


# ---------------------------------------------------------------------------
# PaginatedRecordsResponse
# ---------------------------------------------------------------------------


class TestPaginatedRecordsResponse:
    def test_parses_with_num_records(self):
        data = {
            "success": True,
            "records": [{"name": "p", "value": 1}],
            "numRecords": 50,
        }
        resp = PaginatedRecordsResponse[SampleItem](**data)
        assert resp.success is True
        assert len(resp.records) == 1
        assert resp.num_records == 50

    def test_raw_preserved(self):
        data = {
            "success": True,
            "records": [],
            "numRecords": 0,
        }
        resp = PaginatedRecordsResponse[SampleItem](**data)
        assert resp._raw == data

    def test_is_subclass_of_records_list(self):
        data = {
            "success": True,
            "records": [],
            "numRecords": 0,
        }
        resp = PaginatedRecordsResponse[SampleItem](**data)
        assert isinstance(resp, RecordsListResponse)

    def test_missing_num_records_raises(self):
        with pytest.raises(ValidationError):
            PaginatedRecordsResponse[SampleItem](success=True, records=[])
