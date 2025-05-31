import logging
from datetime import datetime
from typing import Optional, Dict, Any

from vrmapi_async.utils import datetime_to_epoch
from vrmapi_async.client.base.api import BaseNamespace
from .schema import (
    ConsumptionStatsResponse,
    ListUsersResponse,
)


logger = logging.getLogger(__name__)


class InstallationsNamespace(BaseNamespace):

    async def get_consumption_stats(
        self,
        site_id: int,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> ConsumptionStatsResponse:
        """
        Fetches consumption statistics for a given site.

        :param site_id: The installation ID.
        :param start: Optional start datetime (UTC if naive).
        :param end: Optional end datetime (UTC if naive).
        :returns: A ConsumptionStatsResponse object.
        """
        params: Dict[str, Any] = {"type": "consumption"}
        if start:
            params["start"] = datetime_to_epoch(start)
        if end:
            params["end"] = datetime_to_epoch(end)

        url = self.routes.INSTALLATIONS_STATS.format(site_id=site_id)
        response_data = await self._request("GET", url, params=params)
        return ConsumptionStatsResponse(**response_data)

    async def list_users(self, site_id: int) -> ListUsersResponse:
        logger.warning(
            "`list_users` endpoint is not documented in the official VRM API docs"
        )
        url = self.routes.INSTALLATIONS_USERS_LIST.format(site_id=site_id)
        response_data = await self._request("GET", url)
        return ListUsersResponse(**response_data)
