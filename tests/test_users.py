"""Tests for UsersNamespace — all mocked via respx."""

import json

import httpx
import pytest
import respx

from vrmapi_async.client.users.schema import (
    AboutMeResponse,
    AccessToken,
    CreateAccessTokenResponse,
    CreateInstallationResponse,
    InstallationSearchResponse,
    InstallationSearchResult,
    RevokeAccessTokenResponse,
    Site,
    SiteExtended,
    SiteIdByIdentifierResponse,
    User,
    UserSitesExtendedResponse,
    UserSitesResponse,
    UsersListAccessTokensResponse,
)

pytestmark = pytest.mark.asyncio

BASE = "https://vrmapi.victronenergy.com/v2"
USER_ID = 42


# ---------------------------------------------------------------------------
# Fixture data — realistic JSON payloads captured from VRM API
# ---------------------------------------------------------------------------

ABOUT_ME_PAYLOAD = {
    "success": True,
    "user": {
        "id": 42,
        "name": "Test User",
        "email": "test@example.com",
        "country": "CZ",
        "idAccessToken": None,
    },
}

SITE_RECORD = {
    "idSite": 1001,
    "accessLevel": 1,
    "owner": True,
    "isAdmin": True,
    "name": "My Solar Site",
    "identifier": "abc123",
    "idUser": USER_ID,
    "pvMax": 5000,
    "timezone": "Europe/Prague",
    "phonenumber": None,
    "notes": None,
    "geofence": None,
    "geofenceEnabled": False,
    "realtimeUpdates": True,
    "hasMains": True,
    "hasGenerator": False,
    "noDataAlarmTimeout": None,
    "alarmMonitoring": 1,
    "invalidVRMAuthTokenUsedInLogRequest": False,
    "syscreated": 1700000000,
    "shared": False,
    "deviceIcon": "solar",
    "isPaygo": False,
    "paygoCurrency": None,
    "paygoTotalAmount": None,
    "idCurrency": None,
    "currencyCode": None,
    "currencySign": None,
    "currencyName": None,
    "inverterChargerControl": False,
}

SITE_EXTENDED_RECORD = {
    **SITE_RECORD,
    "alarm": False,
    "lastTimestamp": 1700001000,
    "currentTime": "2024-01-15 12:00:00",
    "timezoneOffset": 3600,
    "demoMode": False,
    "mqttWebhost": "mqtt.example.com",
    "mqttHost": "mqtt-internal.example.com",
    "highWorkload": False,
    "currentAlarms": [],
    "numAlarms": 0,
    "tags": [],
    "images": [],
    "viewPermissions": {
        "updateSettings": True,
        "settings": True,
        "diagnostics": True,
        "share": True,
        "mqttRpc": True,
        "vebus": True,
        "twoway": True,
        "exactLocation": True,
        "nodered": True,
        "noderedDash": True,
        "signalk": True,
        "canAlterInstallation": True,
        "canSeeGroupAndTeamMembers": True,
        "dessConfig": False,
        "noderedDashV2": True,
        "paygo": False,
        "rcClassic": True,
        "rcGuiV2": True,
        "readonlyRealtime": False,
    },
    "extended": [],
    "newTags": False,
    "noderedRunning": False,
}

ACCESS_TOKEN_RECORD = {
    "idAccessToken": 99,
    "name": "my-token",
    "createdOn": 1700000000,
    "scope": "all",
    "expires": None,
    "lastSeen": 1700001000,
    "lastSuccessfulAuth": 1700001000,
}

SEARCH_RESULT_RECORD = {
    "siteId": 1001,
    "siteIdentifier": "abc123",
    "siteName": "My Solar Site",
    "avatarUrl": None,
    "highlight": {"siteName": ["<em>My</em> Solar Site"]},
}


# ---------------------------------------------------------------------------
# about_me
# ---------------------------------------------------------------------------


class TestAboutMe:
    async def test_returns_parsed_response(self, mock_api):
        respx.get(f"{BASE}/users/me").mock(
            return_value=httpx.Response(200, json=ABOUT_ME_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.users.about_me()

        assert isinstance(resp, AboutMeResponse)
        assert resp.success is True
        assert isinstance(resp.user, User)
        assert resp.user.user_id == 42
        assert resp.user.name == "Test User"
        assert resp.user.email == "test@example.com"

    async def test_raw_preserved(self, mock_api):
        respx.get(f"{BASE}/users/me").mock(
            return_value=httpx.Response(200, json=ABOUT_ME_PAYLOAD)
        )
        await mock_api.connect()
        resp = await mock_api.users.about_me()
        assert resp._raw == ABOUT_ME_PAYLOAD


# ---------------------------------------------------------------------------
# list_installations
# ---------------------------------------------------------------------------


class TestListInstallations:
    async def test_returns_site_list(self, mock_api):
        payload = {"success": True, "records": [SITE_RECORD]}
        respx.get(f"{BASE}/users/{USER_ID}/installations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.list_installations(USER_ID)

        assert isinstance(resp, UserSitesResponse)
        assert len(resp.records) == 1
        site = resp.records[0]
        assert isinstance(site, Site)
        assert site.site_id == 1001
        assert site.name == "My Solar Site"
        assert site.identifier == "abc123"
        assert site.user_id == USER_ID

    async def test_empty_records(self, mock_api):
        payload = {"success": True, "records": []}
        respx.get(f"{BASE}/users/{USER_ID}/installations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.list_installations(USER_ID)
        assert resp.records == []


# ---------------------------------------------------------------------------
# list_installations_extended
# ---------------------------------------------------------------------------


class TestListInstallationsExtended:
    async def test_returns_extended_sites(self, mock_api):
        payload = {"success": True, "records": [SITE_EXTENDED_RECORD]}
        respx.get(f"{BASE}/users/{USER_ID}/installations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.list_installations_extended(USER_ID)

        assert isinstance(resp, UserSitesExtendedResponse)
        site = resp.records[0]
        assert isinstance(site, SiteExtended)
        assert site.site_id == 1001
        assert site.alarm is False
        assert site.demo_mode is False

    async def test_extended_param_sent(self, mock_api):
        payload = {"success": True, "records": []}
        respx.get(f"{BASE}/users/{USER_ID}/installations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        await mock_api.users.list_installations_extended(USER_ID)

        request = respx.calls.last.request
        assert "extended=1" in str(request.url)

    async def test_tags_false_coerced_to_empty_list(self, mock_api):
        record = {**SITE_EXTENDED_RECORD, "tags": False, "images": False}
        payload = {"success": True, "records": [record]}
        respx.get(f"{BASE}/users/{USER_ID}/installations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.list_installations_extended(USER_ID)
        assert resp.records[0].tags == []
        assert resp.records[0].images == []


# ---------------------------------------------------------------------------
# search_installations_by_query
# ---------------------------------------------------------------------------


class TestSearchInstallations:
    async def test_returns_results(self, mock_api):
        payload = {"success": True, "count": 1, "results": [SEARCH_RESULT_RECORD]}
        respx.get(f"{BASE}/users/{USER_ID}/search").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.search_installations_by_query(USER_ID, "Solar")

        assert isinstance(resp, InstallationSearchResponse)
        assert resp.count == 1
        result = resp.results[0]
        assert isinstance(result, InstallationSearchResult)
        assert result.site_id == 1001

    async def test_query_param_sent(self, mock_api):
        payload = {"success": True, "count": 0, "results": []}
        respx.get(f"{BASE}/users/{USER_ID}/search").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        await mock_api.users.search_installations_by_query(USER_ID, "test query")

        request = respx.calls.last.request
        assert "query=test" in str(request.url)


# ---------------------------------------------------------------------------
# get_site_id_by_identifier
# ---------------------------------------------------------------------------


class TestGetSiteIdByIdentifier:
    async def test_returns_site_id(self, mock_api):
        payload = {"success": True, "records": {"siteId": 1001}}
        respx.post(f"{BASE}/users/{USER_ID}/get-site-id").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.get_site_id_by_identifier(USER_ID, "abc123")

        assert isinstance(resp, SiteIdByIdentifierResponse)
        assert resp.records.site_id == 1001

    async def test_sends_json_body(self, mock_api):
        """Verify identifier is sent in JSON body, not query params."""
        payload = {"success": True, "records": {"siteId": 1001}}
        respx.post(f"{BASE}/users/{USER_ID}/get-site-id").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        await mock_api.users.get_site_id_by_identifier(USER_ID, "abc123")

        request = respx.calls.last.request
        body = json.loads(request.content)
        assert body["installation_identifier"] == "abc123"
        assert "installation_identifier=" not in str(request.url)


# ---------------------------------------------------------------------------
# create_installation
# ---------------------------------------------------------------------------


class TestCreateInstallation:
    async def test_returns_response(self, mock_api):
        payload = {"success": True, "records": {"siteId": 2002}}
        respx.post(f"{BASE}/users/{USER_ID}/addsite").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.create_installation(USER_ID, "new-ident")

        assert isinstance(resp, CreateInstallationResponse)
        assert resp.records.site_id == 2002

    async def test_sends_json_body(self, mock_api):
        """Verify identifier is sent in JSON body, not query params."""
        payload = {"success": True, "records": {"siteId": 2002}}
        respx.post(f"{BASE}/users/{USER_ID}/addsite").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        await mock_api.users.create_installation(USER_ID, "new-ident")

        request = respx.calls.last.request
        body = json.loads(request.content)
        assert body["installation_identifier"] == "new-ident"
        assert "installation_identifier=" not in str(request.url)


# ---------------------------------------------------------------------------
# list_access_tokens
# ---------------------------------------------------------------------------


class TestListAccessTokens:
    async def test_returns_tokens(self, mock_api):
        payload = {"success": True, "tokens": [ACCESS_TOKEN_RECORD]}
        respx.get(f"{BASE}/users/{USER_ID}/accesstokens/list").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.list_access_tokens(USER_ID)

        assert isinstance(resp, UsersListAccessTokensResponse)
        assert len(resp.tokens) == 1
        token = resp.tokens[0]
        assert isinstance(token, AccessToken)
        assert token.access_token_id == 99
        assert token.name == "my-token"

    async def test_empty_tokens(self, mock_api):
        payload = {"success": True, "tokens": []}
        respx.get(f"{BASE}/users/{USER_ID}/accesstokens/list").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.list_access_tokens(USER_ID)
        assert resp.tokens == []


# ---------------------------------------------------------------------------
# create_access_token
# ---------------------------------------------------------------------------


class TestCreateAccessToken:
    async def test_returns_created_token(self, mock_api):
        payload = {"success": True, "token": "new-token-value", "idAccessToken": 100}
        respx.post(f"{BASE}/users/{USER_ID}/accesstokens/create").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.create_access_token(USER_ID, "my-new-token")

        assert isinstance(resp, CreateAccessTokenResponse)
        assert resp.token == "new-token-value"
        assert resp.access_token_id == 100

    async def test_sends_json_body(self, mock_api):
        """Verify name is sent in JSON body, not query params."""
        payload = {"success": True, "token": "t", "idAccessToken": 101}
        respx.post(f"{BASE}/users/{USER_ID}/accesstokens/create").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        await mock_api.users.create_access_token(USER_ID, "my-new-token")

        request = respx.calls.last.request
        body = json.loads(request.content)
        assert body["name"] == "my-new-token"
        assert "name=" not in str(request.url)

    async def test_datetime_expiry_converted(self, mock_api):
        """Verify datetime expiry is converted to epoch in JSON body."""
        from datetime import datetime, timezone

        payload = {"success": True, "token": "t", "idAccessToken": 101}
        respx.post(f"{BASE}/users/{USER_ID}/accesstokens/create").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        dt = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
        await mock_api.users.create_access_token(USER_ID, "expiring", expiry=dt)

        request = respx.calls.last.request
        body = json.loads(request.content)
        assert body["expiry"] == 1748736000


# ---------------------------------------------------------------------------
# revoke_access_token
# ---------------------------------------------------------------------------


class TestRevokeAccessToken:
    async def test_returns_response(self, mock_api):
        payload = {"success": True, "data": {"removed": 1}}
        respx.delete(f"{BASE}/users/{USER_ID}/accesstokens/99").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        resp = await mock_api.users.revoke_access_token(USER_ID, 99)

        assert isinstance(resp, RevokeAccessTokenResponse)
        assert resp.data.removed == 1
