"""Pydantic models for installation-related API responses."""

from enum import StrEnum
from typing import Any

from pydantic import Field, model_validator

from vrmapi_async.client.base.schema import (
    BaseModel,
    BaseResponseModel,
    BaseUser,
)


class StatsType(StrEnum):
    """Supported stat types for the /installations/{id}/stats endpoint."""

    VENUS = "venus"
    LIVE_FEED = "live_feed"
    CONSUMPTION = "consumption"
    SOLAR_YIELD = "solar_yield"
    KWH = "kwh"
    GENERATOR = "generator"
    GENERATOR_RUNTIME = "generator-runtime"
    CUSTOM = "custom"
    FORECAST = "forecast"


class StatsInterval(StrEnum):
    """Supported time intervals for the stats endpoint.

    Max periods: 15mins/hours -> 31d, days -> 180d,
    weeks -> 140d, months -> 24mo, years -> 5y.
    """

    FIFTEEN_MINS = "15mins"
    HOURS = "hours"
    TWO_HOURS = "2hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class StatsRecord(BaseModel):
    """A single data point from a stats response.

    The VRM API returns arrays of [timestamp, mean] or
    [timestamp, mean, min, max]. The timestamp is typically
    in milliseconds.
    """

    timestamp: int
    mean: float | None = None
    min: float | None = None
    max: float | None = None

    @model_validator(mode="before")
    @classmethod
    def transform_list_to_dict(cls, data: Any) -> Any:
        """Transform a [ts, mean, ...] list into a dictionary.

        Handles 2-element [ts, mean], 3-element [ts, mean, min],
        and 4-element [ts, mean, min, max] arrays.
        """
        if isinstance(data, list) and len(data) in (2, 3, 4):
            d: dict[str, Any] = {"timestamp": data[0], "mean": data[1]}
            if len(data) >= 3:
                d["min"] = data[2]
            if len(data) == 4:
                d["max"] = data[3]
            return d
        if isinstance(data, dict):
            return data
        msg = (
            "Unexpected data format for StatsRecord: "
            f"Expected [ts, mean, ...], got {data!r}"
        )
        raise ValueError(msg)


class StatsResponse(BaseResponseModel):
    """Response model for the generic stats endpoint.

    ``records`` is a dict mapping attribute names (e.g. "Pc", "Bc",
    "Pv") to either a list of data points or ``False`` when no data
    exists for the given timeframe.
    """

    success: bool
    records: dict[str, list[StatsRecord] | bool]
    totals: dict[str, float | bool]

    @model_validator(mode="before")
    @classmethod
    def coerce_records(cls, data: Any) -> Any:
        """Coerce record values — leave ``False`` as-is, parse lists."""
        if isinstance(data, dict) and "records" in data:
            records = data["records"]
            if isinstance(records, dict):
                coerced: dict[str, list[StatsRecord] | bool] = {}
                for key, val in records.items():
                    if val is False or val is True:
                        coerced[key] = val
                    elif isinstance(val, list):
                        coerced[key] = [StatsRecord.model_validate(v) for v in val]
                    else:
                        coerced[key] = val
                data = {**data, "records": coerced}
        return data


class InstanceStats(BaseModel):
    """Stats data for a single device instance."""

    instance: int
    stats: dict[str, list[StatsRecord] | bool]

    @model_validator(mode="before")
    @classmethod
    def coerce_stats(cls, data: Any) -> Any:
        """Coerce stats values — same logic as StatsResponse.coerce_records."""
        if isinstance(data, dict) and "stats" in data:
            stats = data["stats"]
            if isinstance(stats, dict):
                coerced: dict[str, list[StatsRecord] | bool] = {}
                for key, val in stats.items():
                    if val is False or val is True:
                        coerced[key] = val
                    elif isinstance(val, list):
                        coerced[key] = [StatsRecord.model_validate(v) for v in val]
                    else:
                        coerced[key] = val
                data = {**data, "stats": coerced}
        return data


class InstanceTotals(BaseModel):
    """Totals for a single device instance."""

    instance: int
    totals: dict[str, float | bool]


class InstancedStatsResponse(BaseResponseModel):
    """Response model for stats with show_instance=true.

    When ``show_instance`` is set, the VRM API groups records and
    totals by device instance instead of returning a flat dict.
    """

    success: bool
    records: list[InstanceStats]
    totals: list[InstanceTotals]

    @model_validator(mode="before")
    @classmethod
    def normalize_records(cls, data: Any) -> Any:
        """Normalize records from dict-keyed-by-instance to list.

        The VRM API may return records as either a list or a dict
        keyed by instance ID strings.
        """
        if not isinstance(data, dict):
            return data
        for field in ("records", "totals"):
            val = data.get(field)
            if isinstance(val, dict):
                data = {**data, field: list(val.values())}
        return data


class User(BaseUser):
    """VRM user associated with an installation."""

    site_id: int = Field(alias="idSite")
    access_level: int
    receives_alarm_notifications: bool
    avatar_url: str | None = None


class InvitedUser(User):
    """Invited user with an optional creation timestamp."""

    created: int | None = None


class PendingUser(BaseModel):
    """Pending user awaiting invitation acceptance."""


class ListUsersResponse(BaseResponseModel):
    """Response model for listing installation users."""

    success: bool
    users: list[User]
    invites: list[InvitedUser] = []
    pending: list[PendingUser] = []
    user_groups: list[Any] = []
    site_groups: list[Any] = []
