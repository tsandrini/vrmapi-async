import pytest
from httpx import Timeout

from vrmapi_async.exceptions import VRMAuthenticationError
from vrmapi_async.routes import VRMRoutes
from vrmapi_async.client import VRMAsyncAPI

pytestmark = pytest.mark.asyncio


class TestClientOnlineViaDemoAuthNamespace:

    async def test_no_auth_method_raises_error(self):
        """Tests that the client fails when no authentication method is provided"""
        with pytest.raises(ValueError):
            VRMAsyncAPI()

    async def test_multiple_auth_methods_raises_error(self):
        with pytest.raises(ValueError):
            VRMAsyncAPI(demo=True, username="user", password="pass")
        with pytest.raises(ValueError):
            VRMAsyncAPI(demo=True, token="TOKEN", user_id_for_token=1)
        with pytest.raises(ValueError):
            VRMAsyncAPI(
                token="TOKEN", user_id_for_token=1, username="user", password="pass"
            )
        with pytest.raises(ValueError):
            VRMAsyncAPI(
                demo=True,
                token="TOKEN",
                user_id_for_token=1,
                username="user",
                password="pass",
            )

    async def test_demo_login(self):
        """Tests that the client can log in using the demo mode."""
        client = VRMAsyncAPI(demo=True)
        await client.connect()
        assert client._auth_mode == "demo"
        assert client._auth_token is not None
        assert isinstance(client.user_id, int)

    async def test_demo_logout(self):
        """Tests that the client can log out using the demo mode."""
        client = VRMAsyncAPI(demo=True)

        await client.connect()
        assert client._auth_token is not None
        assert isinstance(client.user_id, int)

        await client.disconnect()
        assert client._auth_token is None
        assert client.user_id is None

    async def test_demo_disconnect_without_connect(self):
        """Tests that disconnecting without connecting does not raise an error."""
        client = VRMAsyncAPI(demo=True)
        await client.disconnect()

    async def test_demo_client_extra_args(self):
        """Tests that the client parses various extra arguments in demo mode."""

        class DerivedVRMRoutes(VRMRoutes):
            AUTH_DEMO: str = "/auth/loginAsDemo"
            CUSTOM_ENDPOINT: str = "/custom/endpoint"

        client = VRMAsyncAPI(
            demo=True,
            headers={"Custom-Header": "test"},
            httpx_client_kwargs={"timeout": 11},
            routes_cls=DerivedVRMRoutes,
        )
        await client.connect()
        assert isinstance(client.routes, DerivedVRMRoutes)
        assert client._client._timeout == Timeout(11)
        assert client.global_headers == {
            "Custom-Header": "test",
            "Content-Type": "application/json",
        }
        await client.disconnect()

    async def test_demo_manual_request(self):
        """Tests that the client can make a manual request in demo mode."""
        client = VRMAsyncAPI(demo=True)
        await client.connect()
        url = client.routes.USERS_INSTALLATIONS_LIST.format(user_id=client.user_id)
        response_data = await client._request("GET", url)
        assert response_data["success"] is True
        assert isinstance(response_data["records"], list)
        await client.disconnect()

    async def test_demo_manual_request_unauthenticated_raises_error(self):
        """Tests that an unauthenticated request raises an error."""
        client = VRMAsyncAPI(demo=True)
        url = client.routes.USERS_INSTALLATIONS_LIST.format(user_id=client.user_id)
        with pytest.raises(VRMAuthenticationError):
            await client._request("GET", url)


# class TestClientOnlineViaDemoUsersNamespace:
#
#     async def test_get_user_sites_online(self):
#         """Tests fetching non-extended sites from the *real* demo API."""
#         client = VRMAsyncAPI(demo=True)
#         async with client:
#             sites = await client.users.list_installations(client.user_id)
#
#         assert isinstance(sites, list)
#         assert len(sites) > 0
#         assert isinstance(sites[0], Site)
#         # Check if a known field exists and has the right type
#         assert isinstance(sites[0].id_site, int)
#         assert isinstance(sites[0].name, str)
#
#
#     async def test_get_user_sites_extended_online(self):
#         """Tests fetching extended sites from the *real* demo API."""
#         client = VRMAsyncAPI(demo=True)
#         async with client:
#             sites = await client.users.list_installations_extended(client.user_id)
#
#         assert isinstance(sites, list)
#         assert len(sites) > 0  # Demo user should have sites
#         assert isinstance(sites[0], SiteExtended)
#         assert isinstance(sites[0].id_site, int)
#         # Extended response often includes 'tags'
#         assert hasattr(sites[0], "tags")
#
#
#     async def test_get_consumption_stats_online(self):
#         """Tests fetching consumption stats from the *real* demo API."""
#         client = VRMAsyncAPI(demo=True)
#         async with client:
#             # We need a site ID known to be in the demo account. Let's use 2286
#             stats = await client.installations.get_consumption_stats(DEMO_SITE_ID)
#
#         assert isinstance(stats, ConsumptionStatsResponse)
#         assert stats.success is True
#         assert stats.records is not None
#         # We can't guarantee 'Pc' will exist, but we can check the structure
#         assert hasattr(stats.records, "pc") or hasattr(stats.records, "bc")
