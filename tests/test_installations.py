"""Tests for InstallationsNamespace — all mocked via respx."""

from datetime import datetime, timezone

import httpx
import pytest
import respx

from vrmapi_async.client.installations.schema import (
    ConsumptionData,
    ConsumptionStatsResponse,
    ListUsersResponse,
    StatsRecord,
)
from vrmapi_async.client.installations.schema import User as InstallationUser

BASE = "https://vrmapi.victronenergy.com/v2"
SITE_ID = 1001


# ---------------------------------------------------------------------------
# Fixture data
# ---------------------------------------------------------------------------

CONSUMPTION_STATS_PAYLOAD = {
    "success": True,
    "records": {
        "Pc": [[1700000000, 1.5], [1700003600, 2.3]],
        "Bc": [[1700000000, 0.8], [1700003600, 1.1]],
        "Gc": False,
        "gc": False,
    },
    "totals": {"Pc": 3.8, "Bc": 1.9, "Gc": False},
}

LIST_USERS_PAYLOAD = {
    "success": True,
    "users": [
        {
            "idUser": 42,
            "name": "Test User",
            "email": "test@example.com",
            "country": "CZ",
            "idSite": SITE_ID,
            "accessLevel": 1,
            "receivesAlarmNotifications": True,
            "avatarUrl": None,
        },
    ],
    "invites": [],
    "pending": [],
    "userGroups": [],
    "siteGroups": [],
}


# ---------------------------------------------------------------------------
# get_consumption_stats
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestGetConsumptionStats:
    async def test_returns_parsed_response(self, mock_api):
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_consumption_stats(SITE_ID)

        assert isinstance(resp, ConsumptionStatsResponse)
        assert resp.success is True
        assert isinstance(resp.records, ConsumptionData)

    async def test_pc_records_parsed_from_lists(self, mock_api):
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_consumption_stats(SITE_ID)

        assert isinstance(resp.records.pc, list)
        assert len(resp.records.pc) == 2
        rec = resp.records.pc[0]
        assert isinstance(rec, StatsRecord)
        assert rec.timestamp == 1700000000
        assert rec.value == 1.5

    async def test_false_records_preserved(self, mock_api):
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_consumption_stats(SITE_ID)

        assert resp.records.gc is False

    async def test_type_param_sent(self, mock_api):
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        await mock_api.installations.get_consumption_stats(SITE_ID)

        request = respx.calls.last.request
        assert "type=consumption" in str(request.url)

    async def test_datetime_params_converted_to_epoch(self, mock_api):
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        await mock_api.installations.get_consumption_stats(
            SITE_ID, start=start, end=end
        )

        request = respx.calls.last.request
        url_str = str(request.url)
        assert "start=1704067200" in url_str
        assert "end=1706745599" in url_str

    async def test_without_date_range(self, mock_api):
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        await mock_api.installations.get_consumption_stats(SITE_ID)

        url_str = str(respx.calls.last.request.url)
        assert "start=" not in url_str
        assert "end=" not in url_str

    async def test_totals_preserved(self, mock_api):
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_consumption_stats(SITE_ID)
        assert resp.totals["Pc"] == 3.8


# ---------------------------------------------------------------------------
# list_users
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestListUsers:
    async def test_returns_parsed_users(self, mock_api):
        respx.get(f"{BASE}/installations/{SITE_ID}/users").mock(
            return_value=httpx.Response(200, json=LIST_USERS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.list_users(SITE_ID)

        assert isinstance(resp, ListUsersResponse)
        assert resp.success is True
        assert len(resp.users) == 1
        user = resp.users[0]
        assert isinstance(user, InstallationUser)
        assert user.user_id == 42
        assert user.site_id == SITE_ID
        assert user.receives_alarm_notifications is True

    async def test_empty_lists(self, mock_api):
        payload = {
            "success": True,
            "users": [],
            "invites": [],
            "pending": [],
            "userGroups": [],
            "siteGroups": [],
        }
        respx.get(f"{BASE}/installations/{SITE_ID}/users").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.installations.list_users(SITE_ID)
        assert resp.users == []
        assert resp.invites == []


# ---------------------------------------------------------------------------
# StatsRecord model
# ---------------------------------------------------------------------------


class TestStatsRecordModel:
    def test_from_list(self):
        rec = StatsRecord.model_validate([1700000000, 2.5])
        assert rec.timestamp == 1700000000
        assert rec.value == 2.5

    def test_from_dict(self):
        rec = StatsRecord.model_validate({"timestamp": 1700000000, "value": 2.5})
        assert rec.timestamp == 1700000000

    def test_null_value(self):
        rec = StatsRecord.model_validate([1700000000, None])
        assert rec.value is None

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Unexpected data format"):
            StatsRecord.model_validate([1, 2, 3])

    def test_string_raises(self):
        with pytest.raises(ValueError, match="Unexpected data format"):
            StatsRecord.model_validate("not a record")
