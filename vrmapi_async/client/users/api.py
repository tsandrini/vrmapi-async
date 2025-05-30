import logging
from datetime import datetime
from typing import Optional, Dict, Any

from vrmapi_async.utils import datetime_to_epoch
from vrmapi_async.client.base.api import BaseNamespace
from .schema import (
    UserSitesResponse,
    UserSitesExtendedResponse,
    UsersListAccessTokensResponse,
    CreateAccessTokenResponse,
    AboutMeResponse,
    SiteIdByIdentifierResponse,
    InstallationSearchResponse,
    CreateInstallationResponse,
    RevokeAccessTokenResponse,
)


logger = logging.getLogger(__name__)


class UsersNamespace(BaseNamespace):

    async def about_me(self) -> AboutMeResponse:
        """
        Fetches information about the currently authenticated user.

        :returns: AboutMeResponse containing user information
        """
        url = self.routes.USERS_ABOUTME
        response_data = await self._request("GET", url)
        return AboutMeResponse(**response_data)

    async def create_installation(
        self, user_id: int, identifier: str
    ) -> CreateInstallationResponse:
        logger.warning("TODO: UNTESTED")
        url = self.routes.USERS_INSTALLATIONS_CREATE.format(user_id=user_id)
        params = {"installation_identifier": identifier}
        response_data = await self._request("POST", url, params=params)
        return CreateInstallationResponse(**response_data)

    async def search_installations_by_query(
        self, user_id: int, query: str
    ) -> InstallationSearchResponse:
        """
        Filters the user's installations by a search query that can match
        against "any" (most) of the fields in the installation.
        For more info regarding the search query, see the API documentation.

        :param user_id: user_id of the user to search installations for
        :param query: Search query string
        :returns: InstallationSearchResponse containing a list of InstallationSearchResult objects
        """
        url = self.routes.USERS_INSTALLATIONS_SEARCH.format(user_id=user_id)
        params = {"query": query}
        response_data = await self._request("GET", url, params=params)
        return InstallationSearchResponse(**response_data)

    async def get_site_id_by_identifier(
        self, user_id: int, identifier: str
    ) -> SiteIdByIdentifierResponse:
        """
        Gets the site ID for a user by their installation identifier.

        :returns: SiteIdByIdentifierResponse containing the SiteId object
        """
        url = self.routes.USERS_INSTALLATIONS_ID_BY_IDENTIFIER.format(user_id=user_id)
        params = {"installation_identifier": identifier}
        response_data = await self._request("POST", url, params=params)
        return SiteIdByIdentifierResponse(**response_data)

    async def list_installations(self, user_id: int) -> UserSitesResponse:
        """
        Fetches the NON-EXTENDED list of sites for the user.

        :param user_id: user_id of the user to fetch sites for
        :returns: UserSitesResponse containing a list of Site objects
        """
        url = self.routes.USERS_INSTALLATIONS_LIST.format(user_id=user_id)
        response_data = await self._request("GET", url)
        return UserSitesResponse(**response_data)

    async def list_installations_extended(
        self, user_id: int
    ) -> UserSitesExtendedResponse:
        """
        Fetches the EXTENDED list of sites for the user.

        :param user_id: user_id of the user to fetch sites for
        :returns: UserSitesExtendedResponse containing a list of SiteExtended objects
        """
        url = self.routes.USERS_INSTALLATIONS_LIST.format(user_id=user_id)
        params = {"extended": "1"}
        response_data = await self._request("GET", url, params=params)
        return UserSitesExtendedResponse(**response_data)

    async def list_access_tokens(self, user_id: int) -> UsersListAccessTokensResponse:
        """
        Lists all access tokens for the user.

        :param user_id: user_id of the user to fetch access tokens for
        :returns: UsersListAccessTokensResponse containing a list of AccessToken objects
        """
        url = self.routes.USERS_ACCESSTOKENS_LIST.format(user_id=user_id)
        response_data = await self._request("GET", url)
        return UsersListAccessTokensResponse(**response_data)

    async def create_access_token(
        self, user_id: int, name: str, expiry: Optional[int | datetime] = None
    ) -> CreateAccessTokenResponse:
        """
        Creates a new access token for the user.

        :param user_id: user_id of the user to create an access token for
        :param name: Name for the new access token
        :param expiry: Optional expiry time for the token, can be an int (epoch time) or a datetime object
        :returns: CreateAccessTokenResponse containing the created AccessToken object
        """
        logger.warning(
            "The create_access_token endpoint seems to be currently broken in the API."
        )
        url = self.routes.USERS_ACCESSTOKENS_CREATE.format(user_id=user_id)
        params: Dict[str, Any] = {"name": name}
        if expiry:
            params["expiry"] = (
                datetime_to_epoch(expiry) if isinstance(expiry, datetime) else expiry
            )

        response_data = await self._request("POST", url, params=params)
        return CreateAccessTokenResponse(**response_data)

    async def revoke_access_token(
        self, user_id: int, id_access_token: int
    ) -> RevokeAccessTokenResponse:
        """
        Revokes an access token for the user by its id_access_token.

        :param user_id: user_id of the user to revoke the access token for
        :param id_access_token: The ID of the access token to revoke
        :returns: RevokeAccessTokenResponse indicating the success of the operation
        """
        url = self.routes.USERS_ACCESSTOKENS_REVOKE.format(
            user_id=user_id, id_access_token=id_access_token
        )
        response_data = await self._request("GET", url)
        return RevokeAccessTokenResponse(**response_data)
