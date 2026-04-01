"""Main asynchronous client for the Victron VRM API."""

import logging
from types import TracebackType
from typing import Any, Self

import httpx

from vrmapi_async.client.installations.api import InstallationsNamespace
from vrmapi_async.client.schema import DemoLoginResponse, LoginResponse
from vrmapi_async.client.users.api import UsersNamespace
from vrmapi_async.exceptions import VRMAPIRequestError, VRMAuthenticationError
from vrmapi_async.routes import VRMRoutes

logger = logging.getLogger(__name__)

DEMO_USER_ID = 22
DEMO_SITE_ID = 151734


class VRMAsyncAPI:
    """Asynchronous Python client for the Victron VRM API."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        demo: bool = False,
        token: str | None = None,
        user_id_for_token: int | None = None,
        base_url: str = "https://vrmapi.victronenergy.com/v2",
        headers: dict[str, str] | None = None,
        routes_cls: type[VRMRoutes] = VRMRoutes,
        httpx_client_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the VRM API client.

        Authenticate via one of 3 mutually exclusive methods:

        1. Credentials: pass ``username`` and ``password``.
        2. Demo: set ``demo=True`` to use the demo account.
        3. Token: pass ``token`` and ``user_id_for_token``.

        :param username: VRM portal username for credentials auth.
        :param password: VRM portal password for credentials auth.
        :param demo: Set to True to use the demo account.
        :param token: Pre-configured API token for authentication.
        :param user_id_for_token: User ID associated with the token.
        :param base_url: The base URL for the VRM API.
        :param headers: Global headers for all requests.
        :param routes_cls: Custom routes class to override defaults.
        :param httpx_client_kwargs: Extra kwargs for httpx.AsyncClient.
        :raises ValueError: If auth method is missing or ambiguous.
        """
        if httpx_client_kwargs is None:
            httpx_client_kwargs = {}

        auth_methods = sum(
            [
                1 if (username and password) else 0,
                1 if demo else 0,
                1 if (token and user_id_for_token is not None) else 0,
            ]
        )

        if auth_methods == 0:
            msg = (
                "No authentication method provided. "
                "Please provide (username/password), demo=True, "
                "or (token/user_id_for_token)."
            )
            raise ValueError(msg)
        if auth_methods > 1:
            msg = (
                "Multiple authentication methods provided. "
                "Please provide only one: (username/password), "
                "demo=True, or (token/user_id_for_token)."
            )
            raise ValueError(msg)

        if (token and not user_id_for_token) or (not token and user_id_for_token):
            msg = (
                "To properly use token authentication, both "
                "'token' and 'user_id_for_token' must be provided."
            )
            raise ValueError(msg)

        if (username and not password) or (not username and password):
            msg = (
                "To properly use credentials authentication, both "
                "'username' and 'password' must be provided."
            )
            raise ValueError(msg)

        self.username = username
        self.password = password
        self.is_demo = demo
        self._pre_auth_token = token
        self._pre_auth_user_id = user_id_for_token

        self.user_id: int | None = None
        self._auth_token: str | None = None

        self.global_headers = {"Content-Type": "application/json"}
        self.routes = routes_cls()

        self._client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=base_url, **httpx_client_kwargs
        )

        if headers:
            self.global_headers.update(headers)

        if self._pre_auth_token:
            self._auth_mode = "token"
        elif self.is_demo:
            self._auth_mode = "demo"
        else:
            self._auth_mode = "login"

        self.users = UsersNamespace(self._request, self.routes)
        self.installations = InstallationsNamespace(self._request, self.routes)

    async def _login(self) -> None:
        """Log in using username and password."""
        logger.info("Attempting to log in with username %s", self.username)
        try:
            response = await self._client.post(
                self.routes.AUTH_LOGIN,
                json={
                    "username": self.username,
                    "password": self.password,
                },
            )
            response.raise_for_status()
            data = response.json()
            login_data = LoginResponse(**data)
            self._auth_token = login_data.token
            self.user_id = login_data.user_id
            logger.info("Successfully logged in as user %s", self.user_id)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403):
                raise VRMAuthenticationError(
                    "Authentication failed: Check credentials."
                ) from e
            raise VRMAPIRequestError(
                f"Login failed: {e.response.text}",
                e.response.status_code,
                e.response.text,
            ) from e
        except Exception as e:
            raise VRMAPIRequestError(
                f"An unexpected error occurred during login: {e}"
            ) from e

    async def _logout(self) -> None:
        """Log out and invalidate the current session."""
        logger.info("Attempting to log out user %s", self.username)
        if not self._auth_token:
            raise VRMAuthenticationError("No active session to log out from. Exiting.")

        if self._auth_mode == "token":
            raise VRMAuthenticationError(
                "Cannot log out when using token authentication. "
                "To invalidate the token, you must call the "
                "revoke endpoint instead."
            )

        try:
            response = await self._client.post(
                self.routes.AUTH_LOGOUT,
                headers={"X-Authorization": f"Bearer {self._auth_token}"},
            )
            response.raise_for_status()
            logger.info("Successfully logged out user %s", self.username)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise VRMAuthenticationError(
                    "Already logged out or session expired."
                ) from e
            raise VRMAPIRequestError(
                f"Logout failed: {e.response.text}",
                e.response.status_code,
                e.response.text,
            ) from e
        except Exception as e:
            raise VRMAPIRequestError(
                f"An unexpected error occurred during logout: {e}"
            ) from e

    async def _login_as_demo(self) -> None:
        """Log in using the demo account."""
        logger.debug("Attempting to log in as demo.")
        try:
            response = await self._client.get(self.routes.AUTH_DEMO)
            response.raise_for_status()
            data = response.json()
            data["idUser"] = DEMO_USER_ID
            login_data = DemoLoginResponse(**data)
            self._auth_token = login_data.token
            self.user_id = login_data.user_id
            logger.info("Successfully logged in as demo user.")
        except httpx.HTTPStatusError as e:
            raise VRMAPIRequestError(
                f"Demo login failed: {e.response.text}",
                e.response.status_code,
                e.response.text,
            ) from e
        except Exception as e:
            raise VRMAPIRequestError(
                f"An unexpected error occurred during demo login: {e}"
            ) from e

    async def connect(self) -> None:
        """Establish connection and authenticate to the API."""
        logger.debug(
            "Connecting to VRM API with auth mode: %s",
            self._auth_mode,
        )
        if self._auth_mode == "token":
            self._auth_token = self._pre_auth_token
            self.user_id = self._pre_auth_user_id
            logger.info(
                "Using pre-configured API token for user %s",
                self.user_id,
            )
        elif self._auth_mode == "demo":
            await self._login_as_demo()
        else:
            await self._login()

    async def disconnect(self) -> None:
        """Log out (if applicable) and close the HTTP client session."""
        logger.debug("Attempting to disconnect from VRM API")
        if (self._auth_mode in {"login", "demo"}) and self._auth_token:
            await self._logout()

        self._auth_token = None
        self.user_id = None
        if not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self) -> Self:
        """Async context manager entry: connect and return self."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit: close the client."""
        await self.disconnect()

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request with error handling.

        :param method: HTTP method (GET, POST, etc.)
        :param url: The endpoint URL to request.
        :param params: Optional query parameters.
        :param json_data: Optional JSON body.
        :param headers: Optional additional headers.
        :returns: Parsed JSON response as a dictionary.
        :raises VRMAPIRequestError: If the request fails.
        """
        if not self._auth_token:
            raise VRMAuthenticationError("Not logged in. Call connect() first.")

        request_headers = self.global_headers.copy()
        request_headers["X-Authorization"] = (
            "Token " if self._auth_mode == "token" else "Bearer "
        ) + self._auth_token

        if headers:
            request_headers.update(headers)

        logger.debug(
            "Sending %s request to %s with params %s",
            method,
            url,
            params,
        )

        try:
            response = await self._client.request(
                method,
                url,
                headers=request_headers,
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            json_response = response.json()

            if isinstance(json_response, dict) and not json_response.get(
                "success", True
            ):
                raise VRMAPIRequestError(
                    "API indicated failure: "
                    f"{json_response.get('errors', 'Unknown error')}",
                    response.status_code,
                    response.text,
                )
            return json_response

        except httpx.HTTPStatusError as e:
            raise VRMAPIRequestError(
                f"API request failed: {e.response.text}",
                e.response.status_code,
                e.response.text,
            ) from e
        except Exception as e:
            raise VRMAPIRequestError(
                f"An unexpected error occurred during request: {e}"
            ) from e
