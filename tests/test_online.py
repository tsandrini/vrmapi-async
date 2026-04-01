"""Smoke tests against the real VRM demo API.

Skipped by default — run with: pytest -m online
"""

import pytest

from vrmapi_async.client import VRMAsyncAPI
from vrmapi_async.client.users.schema import AboutMeResponse, User, UserSitesResponse

pytestmark = [pytest.mark.asyncio, pytest.mark.online]


class TestDemoAuth:
    async def test_login_and_logout(self):
        client = VRMAsyncAPI(demo=True)
        await client.connect()
        assert client._auth_mode == "demo"
        assert client._auth_token is not None
        assert isinstance(client.user_id, int)

        await client.disconnect()
        assert client._auth_token is None
        assert client.user_id is None

    async def test_context_manager(self):
        async with VRMAsyncAPI(demo=True) as client:
            assert client._auth_token is not None
        assert client._auth_token is None


class TestDemoUsersNamespace:
    async def test_about_me(self):
        async with VRMAsyncAPI(demo=True) as client:
            resp = await client.users.about_me()
        assert isinstance(resp, AboutMeResponse)
        assert resp.success is True
        assert isinstance(resp.user, User)

    async def test_list_installations(self):
        async with VRMAsyncAPI(demo=True) as client:
            assert client.user_id is not None
            resp = await client.users.list_installations(client.user_id)
        assert isinstance(resp, UserSitesResponse)
        assert resp.success is True
        assert len(resp.records) > 0
