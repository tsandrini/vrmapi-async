"""Pydantic models for installation-related API responses."""

from typing import Any

from pydantic import Field, model_validator

from vrmapi_async.client.base.schema import BaseModel, BaseResponseModel, BaseUser


class StatsRecord(BaseModel):
    """A single [timestamp, value] data point from a stats response.

    The timestamp is typically in milliseconds.
    """

    timestamp: int
    value: float | None  # Sometimes value can be null

    @model_validator(mode="before")
    @classmethod
    def transform_list_to_dict(cls, data: Any) -> Any:
        """Transform a [timestamp, value] list into a dictionary.

        Runs before Pydantic validation to normalize the input.
        """
        if isinstance(data, list) and len(data) == 2:
            return {"timestamp": data[0], "value": data[1]}
        if isinstance(data, dict):
            return data
        raise ValueError(
            f"Unexpected data format for StatsRecord: Expected [ts, val], got {data!r}"
        )


class ConsumptionData(BaseModel):
    """Model for the 'records' part of consumption/kwh stats."""

    pc: list[StatsRecord] | bool | None = Field(None, alias="Pc")
    bc: list[StatsRecord] | bool | None = Field(None, alias="Bc")
    gc: Any = Field(alias="Gc")
    gc_lower: Any = Field(alias="gc")

    @model_validator(mode="before")
    @classmethod
    def handle_false_records(cls, data: Any) -> Any:
        """Handle fields that return ``false`` instead of a list.

        Pydantic needs help when a field can be List[Model] or bool.
        If a field is bool, Pydantic might try to validate it against
        StatsRecord. For now, we trust Union.
        """
        return data


class ConsumptionStatsResponse(BaseResponseModel):
    """Response model for consumption/kwh stats."""

    success: bool
    records: ConsumptionData
    totals: dict[str, Any]


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
