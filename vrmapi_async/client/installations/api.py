"""Installations API namespace for VRM API client."""

from datetime import datetime
from typing import Any

from vrmapi_async.client.base.api import BaseNamespace
from vrmapi_async.utils import datetime_to_epoch

from .schema import (
    InstancedStatsResponse,
    ListUsersResponse,
    StatsInterval,
    StatsResponse,
    StatsType,
)


class InstallationsNamespace(BaseNamespace):
    """Namespace for installation-related API operations."""

    async def get_stats(
        self,
        site_id: int,
        stats_type: StatsType = StatsType.LIVE_FEED,
        interval: StatsInterval | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        attribute_codes: list[str] | None = None,
    ) -> StatsResponse:
        """Fetch statistics for a given site.

        :param site_id: The installation ID.
        :param stats_type: Type of stats to fetch (default: live_feed).
        :param interval: Time interval between data points.
        :param start: Optional start datetime (UTC if naive).
        :param end: Optional end datetime (UTC if naive).
        :param attribute_codes: Attribute codes for custom type.
        :returns: A StatsResponse with dynamic attribute keys.
        """
        params: dict[str, Any] = {"type": str(stats_type)}
        if interval:
            params["interval"] = str(interval)
        if start:
            params["start"] = datetime_to_epoch(start)
        if end:
            params["end"] = datetime_to_epoch(end)
        if attribute_codes:
            params["attributeCodes[]"] = attribute_codes

        url = self.routes.INSTALLATIONS_STATS.format(site_id=site_id)
        response_data = await self._request("GET", url, params=params)
        return StatsResponse(**response_data)

    async def get_stats_by_instance(
        self,
        site_id: int,
        stats_type: StatsType = StatsType.LIVE_FEED,
        interval: StatsInterval | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        attribute_codes: list[str] | None = None,
    ) -> InstancedStatsResponse:
        """Fetch statistics grouped by device instance.

        Same as :meth:`get_stats` but with ``show_instance=1``,
        which causes the VRM API to group records and totals by
        device instance.

        :param site_id: The installation ID.
        :param stats_type: Type of stats to fetch (default: live_feed).
        :param interval: Time interval between data points.
        :param start: Optional start datetime (UTC if naive).
        :param end: Optional end datetime (UTC if naive).
        :param attribute_codes: Attribute codes for custom type.
        :returns: An InstancedStatsResponse grouped by instance.
        """
        params: dict[str, Any] = {"type": str(stats_type), "show_instance": 1}
        if interval:
            params["interval"] = str(interval)
        if start:
            params["start"] = datetime_to_epoch(start)
        if end:
            params["end"] = datetime_to_epoch(end)
        if attribute_codes:
            params["attributeCodes[]"] = attribute_codes

        url = self.routes.INSTALLATIONS_STATS.format(site_id=site_id)
        response_data = await self._request("GET", url, params=params)
        return InstancedStatsResponse(**response_data)

    async def get_consumption_stats(
        self,
        site_id: int,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> StatsResponse:
        """Fetch consumption statistics for a given site.

        Convenience wrapper around :meth:`get_stats` with
        ``type=consumption``.

        :param site_id: The installation ID.
        :param start: Optional start datetime (UTC if naive).
        :param end: Optional end datetime (UTC if naive).
        :returns: A StatsResponse with consumption attribute keys.
        """
        return await self.get_stats(
            site_id,
            stats_type=StatsType.CONSUMPTION,
            start=start,
            end=end,
        )

    async def list_users(self, site_id: int) -> ListUsersResponse:
        """List users for a given installation.

        Returns all users, pending invites, pending access requests,
        user groups, and site groups linked to the installation.
        Requires full control or technician access level.

        :param site_id: The installation ID.
        :returns: A ListUsersResponse with users, invites, pending, etc.
        """
        url = self.routes.INSTALLATIONS_USERS_LIST.format(site_id=site_id)
        response_data = await self._request("GET", url)
        return ListUsersResponse(**response_data)
