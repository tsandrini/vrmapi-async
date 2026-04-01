"""Users API namespace for VRM API client."""

import logging
from datetime import datetime
from typing import Any

from vrmapi_async.client.base.api import BaseNamespace
from vrmapi_async.utils import datetime_to_epoch

from .schema import (
    AboutMeResponse,
    CreateAccessTokenResponse,
    CreateInstallationResponse,
    InstallationSearchResponse,
    RevokeAccessTokenResponse,
    SiteIdByIdentifierResponse,
    UserSitesExtendedResponse,
    UserSitesResponse,
    UsersListAccessTokensResponse,
)

logger = logging.getLogger(__name__)


class UsersNamespace(BaseNamespace):
    """Namespace for user-related API operations."""

    async def about_me(self) -> AboutMeResponse:
        """Fetch information about the currently authenticated user.

        :returns: AboutMeResponse containing user information.
        """
        url = self.routes.USERS_ABOUTME
        response_data = await self._request("GET", url)
        return AboutMeResponse(**response_data)

    async def create_installation(
        self, user_id: int, identifier: str
    ) -> CreateInstallationResponse:
        """Create a new installation for the user (UNTESTED)."""
        logger.warning("TODO: UNTESTED")
        url = self.routes.USERS_INSTALLATIONS_CREATE.format(user_id=user_id)
        json_data = {"installation_identifier": identifier}
        response_data = await self._request("POST", url, json_data=json_data)
        return CreateInstallationResponse(**response_data)

    async def search_installations_by_query(
        self, user_id: int, query: str
    ) -> InstallationSearchResponse:
        """Filter installations by a search query.

        The query can match against most fields in the installation.
        For more info regarding the search query, see the API docs.

        :param user_id: User ID to search installations for.
        :param query: Search query string.
        :returns: InstallationSearchResponse with matching results.
        """
        url = self.routes.USERS_INSTALLATIONS_SEARCH.format(user_id=user_id)
        params = {"query": query}
        response_data = await self._request("GET", url, params=params)
        return InstallationSearchResponse(**response_data)

    async def get_site_id_by_identifier(
        self, user_id: int, identifier: str
    ) -> SiteIdByIdentifierResponse:
        """Get the site ID for a user by installation identifier.

        :param user_id: User ID to fetch the site ID for.
        :param identifier: The installation identifier to search for.
        :returns: SiteIdByIdentifierResponse containing the SiteId.
        """
        url = self.routes.USERS_INSTALLATIONS_ID_BY_IDENTIFIER.format(user_id=user_id)
        json_data = {"installation_identifier": identifier}
        response_data = await self._request("POST", url, json_data=json_data)
        return SiteIdByIdentifierResponse(**response_data)

    async def list_installations(self, user_id: int) -> UserSitesResponse:
        """Fetch the non-extended list of sites for the user.

        :param user_id: User ID to fetch sites for.
        :returns: UserSitesResponse containing a list of Site objects.
        """
        url = self.routes.USERS_INSTALLATIONS_LIST.format(user_id=user_id)
        response_data = await self._request("GET", url)
        return UserSitesResponse(**response_data)

    async def list_installations_extended(
        self, user_id: int
    ) -> UserSitesExtendedResponse:
        """Fetch the extended list of sites for the user.

        :param user_id: User ID to fetch sites for.
        :returns: UserSitesExtendedResponse with SiteExtended objects.
        """
        url = self.routes.USERS_INSTALLATIONS_LIST.format(user_id=user_id)
        params = {"extended": "1"}
        response_data = await self._request("GET", url, params=params)
        return UserSitesExtendedResponse(**response_data)

    async def list_access_tokens(self, user_id: int) -> UsersListAccessTokensResponse:
        """List all access tokens for the user.

        :param user_id: User ID to fetch access tokens for.
        :returns: UsersListAccessTokensResponse with AccessToken list.
        """
        url = self.routes.USERS_ACCESSTOKENS_LIST.format(user_id=user_id)
        response_data = await self._request("GET", url)
        return UsersListAccessTokensResponse(**response_data)

    async def create_access_token(
        self,
        user_id: int,
        name: str,
        expiry: int | datetime | None = None,
    ) -> CreateAccessTokenResponse:
        """Create a new access token for the user.

        :param user_id: User ID to create an access token for.
        :param name: Name for the new access token.
        :param expiry: Optional expiry (epoch int or datetime).
        :returns: CreateAccessTokenResponse with the created token.
        """
        url = self.routes.USERS_ACCESSTOKENS_CREATE.format(user_id=user_id)
        json_data: dict[str, Any] = {"name": name}
        if expiry:
            json_data["expiry"] = (
                datetime_to_epoch(expiry) if isinstance(expiry, datetime) else expiry
            )

        response_data = await self._request("POST", url, json_data=json_data)
        return CreateAccessTokenResponse(**response_data)

    async def revoke_access_token(
        self, user_id: int, access_token_id: int
    ) -> RevokeAccessTokenResponse:
        """Revoke an access token for the user by its ID.

        :param user_id: User ID to revoke the access token for.
        :param access_token_id: The ID of the access token to revoke.
        :returns: RevokeAccessTokenResponse indicating success.
        """
        url = self.routes.USERS_ACCESSTOKENS_REVOKE.format(
            user_id=user_id, access_token_id=access_token_id
        )
        response_data = await self._request("GET", url)
        return RevokeAccessTokenResponse(**response_data)
