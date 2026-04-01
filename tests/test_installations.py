"""Tests for InstallationsNamespace — all mocked via respx."""

from datetime import datetime, timezone

import httpx
import pytest
import respx

from vrmapi_async.client.installations.schema import (
    InstancedStatsResponse,
    InstanceStats,
    ListUsersResponse,
    StatsRecord,
    StatsResponse,
    StatsType,
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

SOLAR_YIELD_STATS_PAYLOAD = {
    "success": True,
    "records": {
        "Pv": [[1700000000, 5.2, 3.1, 7.8], [1700003600, 4.1, 2.0, 6.5]],
        "total_solar_yield": False,
    },
    "totals": {"Pv": 9.3, "total_solar_yield": False},
}

INSTANCED_STATS_PAYLOAD = {
    "success": True,
    "records": [
        {
            "instance": 0,
            "stats": {
                "Pv": [[1700000000, 3.0, 1.0, 5.0]],
                "Bc": False,
            },
        },
        {
            "instance": 1,
            "stats": {
                "Pv": [[1700000000, 2.2, 1.5, 3.0]],
                "Bc": [[1700000000, 0.5]],
            },
        },
    ],
    "totals": [
        {"instance": 0, "totals": {"Pv": 3.0, "Bc": False}},
        {"instance": 1, "totals": {"Pv": 2.2, "Bc": 0.5}},
    ],
}

INSTANCED_STATS_DICT_PAYLOAD = {
    "success": True,
    "records": {
        "0": {
            "instance": 0,
            "stats": {
                "Pv": [[1700000000, 3.0]],
            },
        },
    },
    "totals": {
        "0": {"instance": 0, "totals": {"Pv": 3.0}},
    },
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
# get_stats
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestGetStats:
    """Tests for the generic get_stats method."""

    async def test_returns_parsed_response(self, mock_api):
        """Verify basic parsing of a consumption stats response."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats(
            SITE_ID, stats_type=StatsType.CONSUMPTION
        )

        assert isinstance(resp, StatsResponse)
        assert resp.success is True
        assert "Pc" in resp.records
        assert "Bc" in resp.records

    async def test_records_parsed_as_stats_records(self, mock_api):
        """Verify list values are parsed into StatsRecord objects."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats(
            SITE_ID, stats_type=StatsType.CONSUMPTION
        )

        pc = resp.records["Pc"]
        assert isinstance(pc, list)
        assert len(pc) == 2
        assert isinstance(pc[0], StatsRecord)
        assert pc[0].timestamp == 1700000000
        assert pc[0].mean == 1.5

    async def test_false_records_preserved(self, mock_api):
        """Verify that False (no data) values pass through unchanged."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats(
            SITE_ID, stats_type=StatsType.CONSUMPTION
        )

        assert resp.records["Gc"] is False

    async def test_four_element_records(self, mock_api):
        """Verify [ts, mean, min, max] arrays are fully parsed."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=SOLAR_YIELD_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats(
            SITE_ID, stats_type=StatsType.SOLAR_YIELD
        )

        pv = resp.records["Pv"]
        assert isinstance(pv, list)
        rec = pv[0]
        assert rec.mean == 5.2
        assert rec.min == 3.1
        assert rec.max == 7.8

    async def test_type_param_sent(self, mock_api):
        """Verify the type query parameter is included."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        await mock_api.installations.get_stats(
            SITE_ID, stats_type=StatsType.CONSUMPTION
        )

        request = respx.calls.last.request
        assert "type=consumption" in str(request.url)

    async def test_interval_param_sent(self, mock_api):
        """Verify the interval query parameter is included when set."""
        from vrmapi_async.client.installations.schema import StatsInterval

        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        await mock_api.installations.get_stats(
            SITE_ID,
            stats_type=StatsType.CONSUMPTION,
            interval=StatsInterval.DAYS,
        )

        request = respx.calls.last.request
        assert "interval=days" in str(request.url)

    async def test_attribute_codes_sent(self, mock_api):
        """Verify attributeCodes[] params are included for custom type."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        await mock_api.installations.get_stats(
            SITE_ID,
            stats_type=StatsType.CUSTOM,
            attribute_codes=["Pv", "Bc"],
        )

        url_str = str(respx.calls.last.request.url)
        assert "attributeCodes" in url_str

    async def test_datetime_params_converted_to_epoch(self, mock_api):
        """Verify datetime start/end are converted to epoch integers."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        await mock_api.installations.get_stats(
            SITE_ID, stats_type=StatsType.CONSUMPTION, start=start, end=end
        )

        url_str = str(respx.calls.last.request.url)
        assert "start=1704067200" in url_str
        assert "end=1706745599" in url_str

    async def test_without_date_range(self, mock_api):
        """Verify no start/end params sent when not provided."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        await mock_api.installations.get_stats(
            SITE_ID, stats_type=StatsType.CONSUMPTION
        )

        url_str = str(respx.calls.last.request.url)
        assert "start=" not in url_str
        assert "end=" not in url_str

    async def test_totals_preserved(self, mock_api):
        """Verify totals dict is preserved in the response."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats(
            SITE_ID, stats_type=StatsType.CONSUMPTION
        )
        assert resp.totals["Pc"] == 3.8
        assert resp.totals["Gc"] is False

    async def test_raw_escape_hatch(self, mock_api):
        """Verify _raw captures the full response dict."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats(
            SITE_ID, stats_type=StatsType.CONSUMPTION
        )
        assert resp._raw["success"] is True
        assert "Pc" in resp._raw["records"]


# ---------------------------------------------------------------------------
# get_consumption_stats (convenience wrapper)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestGetConsumptionStats:
    """Tests for the get_consumption_stats convenience wrapper."""

    async def test_sends_consumption_type(self, mock_api):
        """Verify it sends type=consumption."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        await mock_api.installations.get_consumption_stats(SITE_ID)

        assert "type=consumption" in str(respx.calls.last.request.url)

    async def test_returns_stats_response(self, mock_api):
        """Verify it returns a StatsResponse."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_consumption_stats(SITE_ID)
        assert isinstance(resp, StatsResponse)

    async def test_forwards_date_params(self, mock_api):
        """Verify start/end are forwarded correctly."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=CONSUMPTION_STATS_PAYLOAD)
        )
        await mock_api.connect()
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        await mock_api.installations.get_consumption_stats(SITE_ID, start=start)
        assert "start=1704067200" in str(respx.calls.last.request.url)


# ---------------------------------------------------------------------------
# get_stats_by_instance
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestGetStatsByInstance:
    """Tests for get_stats_by_instance."""

    async def test_returns_instanced_response(self, mock_api):
        """Verify it returns an InstancedStatsResponse."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=INSTANCED_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats_by_instance(
            SITE_ID, stats_type=StatsType.SOLAR_YIELD
        )

        assert isinstance(resp, InstancedStatsResponse)
        assert resp.success is True
        assert len(resp.records) == 2

    async def test_instance_stats_parsed(self, mock_api):
        """Verify per-instance stats are correctly parsed."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=INSTANCED_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats_by_instance(
            SITE_ID, stats_type=StatsType.SOLAR_YIELD
        )

        inst0 = resp.records[0]
        assert isinstance(inst0, InstanceStats)
        assert inst0.instance == 0
        pv = inst0.stats["Pv"]
        assert isinstance(pv, list)
        assert pv[0].mean == 3.0
        assert pv[0].min == 1.0
        assert pv[0].max == 5.0

    async def test_instance_false_records(self, mock_api):
        """Verify False values within instanced stats."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=INSTANCED_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats_by_instance(
            SITE_ID, stats_type=StatsType.SOLAR_YIELD
        )

        assert resp.records[0].stats["Bc"] is False

    async def test_instance_totals_parsed(self, mock_api):
        """Verify per-instance totals are parsed."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=INSTANCED_STATS_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats_by_instance(
            SITE_ID, stats_type=StatsType.SOLAR_YIELD
        )

        assert resp.totals[0].instance == 0
        assert resp.totals[0].totals["Pv"] == 3.0
        assert resp.totals[0].totals["Bc"] is False

    async def test_show_instance_param_sent(self, mock_api):
        """Verify show_instance=1 is included in query params."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=INSTANCED_STATS_PAYLOAD)
        )
        await mock_api.connect()
        await mock_api.installations.get_stats_by_instance(
            SITE_ID, stats_type=StatsType.SOLAR_YIELD
        )

        url_str = str(respx.calls.last.request.url)
        assert "show_instance=1" in url_str

    async def test_dict_keyed_records_normalized(self, mock_api):
        """Verify dict-keyed-by-instance records are normalized to list."""
        respx.get(f"{BASE}/installations/{SITE_ID}/stats").mock(
            return_value=httpx.Response(200, json=INSTANCED_STATS_DICT_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.installations.get_stats_by_instance(
            SITE_ID, stats_type=StatsType.SOLAR_YIELD
        )

        assert isinstance(resp.records, list)
        assert len(resp.records) == 1
        assert resp.records[0].instance == 0


# ---------------------------------------------------------------------------
# list_users
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestListUsers:
    """Tests for list_users."""

    async def test_returns_parsed_users(self, mock_api):
        """Verify users are correctly parsed."""
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
        """Verify empty user lists are handled."""
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
    """Tests for StatsRecord parsing from various formats."""

    def test_from_two_element_list(self):
        """Verify [ts, mean] parsing."""
        rec = StatsRecord.model_validate([1700000000, 2.5])
        assert rec.timestamp == 1700000000
        assert rec.mean == 2.5
        assert rec.min is None
        assert rec.max is None

    def test_from_three_element_list(self):
        """Verify [ts, mean, min] parsing."""
        rec = StatsRecord.model_validate([1700000000, 2.5, 1.0])
        assert rec.mean == 2.5
        assert rec.min == 1.0
        assert rec.max is None

    def test_from_four_element_list(self):
        """Verify [ts, mean, min, max] parsing."""
        rec = StatsRecord.model_validate([1700000000, 2.5, 1.0, 4.0])
        assert rec.mean == 2.5
        assert rec.min == 1.0
        assert rec.max == 4.0

    def test_from_dict(self):
        """Verify dict input passthrough."""
        rec = StatsRecord.model_validate({"timestamp": 1700000000, "mean": 2.5})
        assert rec.timestamp == 1700000000

    def test_null_value(self):
        """Verify null mean is handled."""
        rec = StatsRecord.model_validate([1700000000, None])
        assert rec.mean is None

    def test_single_element_raises(self):
        """Verify single-element list raises."""
        with pytest.raises(ValueError, match="Unexpected data format"):
            StatsRecord.model_validate([1])

    def test_five_element_raises(self):
        """Verify five-element list raises."""
        with pytest.raises(ValueError, match="Unexpected data format"):
            StatsRecord.model_validate([1, 2, 3, 4, 5])

    def test_string_raises(self):
        """Verify string input raises."""
        with pytest.raises(ValueError, match="Unexpected data format"):
            StatsRecord.model_validate("not a record")
