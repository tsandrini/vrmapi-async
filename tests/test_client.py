"""Test VRMAsyncAPI client: constructor validation, auth, and _request."""

import httpx
import pytest
import respx

from vrmapi_async.client import VRMAsyncAPI
from vrmapi_async.exceptions import VRMAPIRequestError, VRMAuthenticationError
from vrmapi_async.routes import VRMRoutes

BASE = "https://vrmapi.victronenergy.com/v2"


# ---------------------------------------------------------------------------
# Constructor validation (sync — no asyncio mark needed)
# ---------------------------------------------------------------------------


class TestConstructorValidation:
    def test_no_auth_method_raises(self):
        with pytest.raises(ValueError, match="No authentication method"):
            VRMAsyncAPI()

    def test_multiple_auth_methods_raises(self):
        with pytest.raises(ValueError, match="Multiple authentication"):
            VRMAsyncAPI(demo=True, username="u", password="p")

        with pytest.raises(ValueError, match="Multiple authentication"):
            VRMAsyncAPI(demo=True, token="t", user_id_for_token=1)

        with pytest.raises(ValueError, match="Multiple authentication"):
            VRMAsyncAPI(token="t", user_id_for_token=1, username="u", password="p")

    def test_token_without_user_id_raises(self):
        with pytest.raises(ValueError, match="user_id_for_token"):
            VRMAsyncAPI(token="t")

    def test_user_id_without_token_raises(self):
        with pytest.raises(ValueError, match="user_id_for_token"):
            VRMAsyncAPI(user_id_for_token=1)

    def test_username_without_password_raises(self):
        with pytest.raises(ValueError, match="password"):
            VRMAsyncAPI(username="u")

    def test_password_without_username_raises(self):
        with pytest.raises(ValueError, match="password"):
            VRMAsyncAPI(password="p")

    def test_token_auth_sets_mode(self):
        client = VRMAsyncAPI(token="t", user_id_for_token=1)
        assert client._auth_mode == "token"

    def test_demo_auth_sets_mode(self):
        client = VRMAsyncAPI(demo=True)
        assert client._auth_mode == "demo"

    def test_credentials_auth_sets_mode(self):
        client = VRMAsyncAPI(username="u", password="p")
        assert client._auth_mode == "login"

    def test_custom_routes_cls(self):
        class CustomRoutes(VRMRoutes):
            CUSTOM: str = "/custom"

        client = VRMAsyncAPI(demo=True, routes_cls=CustomRoutes)
        assert isinstance(client.routes, CustomRoutes)

    def test_custom_headers_merged(self):
        client = VRMAsyncAPI(demo=True, headers={"X-Custom": "val"})
        assert client.global_headers["X-Custom"] == "val"
        assert client.global_headers["Content-Type"] == "application/json"

    def test_httpx_kwargs_forwarded(self):
        client = VRMAsyncAPI(demo=True, httpx_client_kwargs={"follow_redirects": True})
        assert client._client.follow_redirects is True

    def test_default_timeout(self):
        client = VRMAsyncAPI(demo=True)
        assert client._client._timeout == httpx.Timeout(30.0)

    def test_custom_timeout_float(self):
        client = VRMAsyncAPI(demo=True, timeout=10.0)
        assert client._client._timeout == httpx.Timeout(10.0)

    def test_custom_timeout_object(self):
        timeout = httpx.Timeout(5.0, connect=2.0)
        client = VRMAsyncAPI(demo=True, timeout=timeout)
        assert client._client._timeout == timeout

    def test_timeout_none_disables(self):
        client = VRMAsyncAPI(demo=True, timeout=None)
        assert client._client._timeout == httpx.Timeout(None)


# ---------------------------------------------------------------------------
# Connect / disconnect
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestTokenConnect:
    async def test_connect_sets_token_and_user_id(self, mock_api):
        await mock_api.connect()
        assert mock_api._auth_token == "fake-token-for-tests"
        assert mock_api.user_id == 42

    async def test_disconnect_clears_state(self, mock_api):
        await mock_api.connect()
        await mock_api.disconnect()
        assert mock_api._auth_token is None
        assert mock_api.user_id is None

    async def test_context_manager(self, mock_api):
        async with mock_api:
            assert mock_api._auth_token is not None
        assert mock_api._auth_token is None


# ---------------------------------------------------------------------------
# _request — auth header
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestRequestAuthHeaders:
    async def test_token_mode_uses_token_header(self, mock_api):
        respx.get(f"{BASE}/test").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        await mock_api.connect()
        await mock_api._request("GET", "/test")

        request = respx.calls.last.request
        assert request.headers["X-Authorization"] == "Token fake-token-for-tests"

    async def test_bearer_mode_header(self, respx_mock):
        respx_mock.get(f"{BASE}/auth/loginAsDemo").mock(
            return_value=httpx.Response(
                200,
                json={
                    "token": "demo-jwt",
                    "idUser": 22,
                    "verification_mode": "pin",
                    "verification_sent": False,
                },
            )
        )
        respx_mock.get(f"{BASE}/test").mock(
            return_value=httpx.Response(200, json={"ok": True})
        )
        respx_mock.post(f"{BASE}/auth/logout").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        client = VRMAsyncAPI(demo=True, max_retries=0)
        async with client:
            await client._request("GET", "/test")

        test_call = next(c for c in respx_mock.calls if "/test" in str(c.request.url))
        assert test_call.request.headers["X-Authorization"] == "Bearer demo-jwt"

    async def test_request_without_connect_raises(self):
        client = VRMAsyncAPI(token="t", user_id_for_token=1)
        with pytest.raises(VRMAuthenticationError, match="Not logged in"):
            await client._request("GET", "/test")


# ---------------------------------------------------------------------------
# _request — response handling
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestRequestResponseHandling:
    async def test_success_returns_json(self, mock_api):
        payload = {"success": True, "data": [1, 2, 3]}
        respx.get(f"{BASE}/endpoint").mock(
            return_value=httpx.Response(200, json=payload)
        )
        await mock_api.connect()
        result = await mock_api._request("GET", "/endpoint")
        assert result == payload

    async def test_api_success_false_raises(self, mock_api):
        respx.get(f"{BASE}/endpoint").mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": False,
                    "errors": "Something went wrong",
                },
            )
        )
        await mock_api.connect()
        with pytest.raises(VRMAPIRequestError, match="API indicated failure"):
            await mock_api._request("GET", "/endpoint")

    async def test_http_error_raises_with_status(self, mock_api):
        respx.get(f"{BASE}/endpoint").mock(
            return_value=httpx.Response(404, text="Not Found")
        )
        await mock_api.connect()
        with pytest.raises(VRMAPIRequestError) as exc_info:
            await mock_api._request("GET", "/endpoint")
        assert exc_info.value.status_code == 404

    async def test_params_forwarded(self, mock_api):
        respx.get(f"{BASE}/endpoint").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        await mock_api.connect()
        await mock_api._request("GET", "/endpoint", params={"foo": "bar"})

        request = respx.calls.last.request
        assert "foo=bar" in str(request.url)

    async def test_json_body_forwarded(self, mock_api):
        respx.post(f"{BASE}/endpoint").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        await mock_api.connect()
        await mock_api._request("POST", "/endpoint", json_data={"key": "val"})

        request = respx.calls.last.request
        assert b'"key"' in request.content


# ---------------------------------------------------------------------------
# _request — retry behavior
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestRequestRetries:
    async def test_429_retries_then_succeeds(self, mock_api_with_retries):
        route = respx.get(f"{BASE}/endpoint")
        route.side_effect = [
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"success": True}),
        ]
        await mock_api_with_retries.connect()
        result = await mock_api_with_retries._request("GET", "/endpoint")
        assert result["success"] is True
        assert route.call_count == 2

    async def test_429_exhausted_raises(self, mock_api_with_retries):
        route = respx.get(f"{BASE}/endpoint")
        route.side_effect = [
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(429, headers={"Retry-After": "0"}),
        ]
        await mock_api_with_retries.connect()
        # On the last attempt _get_retry_delay returns None (is_last_attempt),
        # so _request raises VRMAPIRequestError directly rather than looping
        # to the exhaustion block.
        with pytest.raises(VRMAPIRequestError):
            await mock_api_with_retries._request("GET", "/endpoint")
        assert route.call_count == 4  # 1 initial + 3 retries

    async def test_5xx_retries_then_succeeds(self, mock_api_with_retries):
        route = respx.get(f"{BASE}/endpoint")
        route.side_effect = [
            httpx.Response(502, text="Bad Gateway"),
            httpx.Response(200, json={"success": True}),
        ]
        await mock_api_with_retries.connect()
        result = await mock_api_with_retries._request("GET", "/endpoint")
        assert result["success"] is True
        assert route.call_count == 2

    async def test_5xx_exhausted_raises(self, mock_api_with_retries):
        route = respx.get(f"{BASE}/endpoint")
        route.side_effect = [
            httpx.Response(503, text="Unavailable"),
            httpx.Response(503, text="Unavailable"),
            httpx.Response(503, text="Unavailable"),
            httpx.Response(503, text="Unavailable"),
        ]
        await mock_api_with_retries.connect()
        with pytest.raises(VRMAPIRequestError) as exc_info:
            await mock_api_with_retries._request("GET", "/endpoint")
        assert exc_info.value.status_code == 503
        assert route.call_count == 4

    async def test_5xx_not_retried_when_disabled(self, respx_mock):
        client = VRMAsyncAPI(
            token="t",
            user_id_for_token=1,
            max_retries=3,
            retry_backoff_base=0.0,
            retry_on_5xx=False,
        )
        respx_mock.get(f"{BASE}/endpoint").mock(
            return_value=httpx.Response(502, text="Bad Gateway")
        )
        await client.connect()
        with pytest.raises(VRMAPIRequestError):
            await client._request("GET", "/endpoint")
        assert respx_mock.calls.call_count == 1

    async def test_no_retry_on_4xx(self, mock_api_with_retries):
        route = respx.get(f"{BASE}/endpoint")
        route.mock(return_value=httpx.Response(403, text="Forbidden"))
        await mock_api_with_retries.connect()
        with pytest.raises(VRMAPIRequestError) as exc_info:
            await mock_api_with_retries._request("GET", "/endpoint")
        assert exc_info.value.status_code == 403
        assert route.call_count == 1
