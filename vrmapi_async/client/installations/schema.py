from pydantic import Field, model_validator
from typing import List, Dict, Any

from vrmapi_async.client.base.schema import BaseModel, BaseResponseModel, BaseUser


class StatsRecord(BaseModel):
    """
    Represents a single [timestamp, value] data point from a stats response.
    The timestamp is typically in milliseconds.
    """

    timestamp: int
    value: float | None  # Sometimes value can be null

    @model_validator(mode="before")
    @classmethod
    def transform_list_to_dict(cls, data: Any) -> Any:
        """
        Transforms a [timestamp, value] list into a dictionary
        before Pydantic validation.
        """
        if isinstance(data, list) and len(data) == 2:
            return {"timestamp": data[0], "value": data[1]}
        if isinstance(data, dict):
            return data
        # If it's not a list or dict, maybe it's the 'False' case -
        # but that should be handled by the Union in the parent model.
        # We raise here if it's not a list, as StatsRecord itself MUST be a list.
        raise ValueError(
            f"Unexpected data format for StatsRecord: Expected [ts, val], got {data!r}"
        )


class ConsumptionData(BaseModel):
    """Model for the 'records' part of consumption/kwh stats."""

    pc: List[StatsRecord] | bool | None = Field(None, alias="Pc")
    bc: List[StatsRecord] | bool | None = Field(None, alias="Bc")
    gc: Any = Field(alias="Gc")
    gc_lower: Any = Field(alias="gc")

    @model_validator(mode="before")
    @classmethod
    def handle_false_records(cls, data: Any) -> Any:
        """
        Pydantic needs help when a field can be List[Model] or bool.
        If a field is bool, Pydantic might try to validate it against StatsRecord.
        This validator isn't strictly necessary if Union works directly, but
        it can help clarify or pre-process if needed. For now, we trust Union.
        If Union fails, we might need a more complex validator here.
        Let's try without an extra validator first, relying on Union.
        """
        # If Union[List[StatsRecord], bool] works directly, this validator
        # might not be needed. Let's start without it and add it back
        # only if Pydantic struggles with the Union type during list validation.
        return data


class ConsumptionStatsResponse(BaseResponseModel):
    """Response model for consumption/kwh stats."""

    success: bool
    records: ConsumptionData
    totals: Dict[str, Any]


class User(BaseUser):
    """
    Represents a VRM user.
    This is a simplified model for the user data.
    """

    site_id: int = Field(alias="idSite")
    access_level: int
    receives_alarm_notifications: bool
    avatar_url: str | None = None


class InvitedUser(User):
    created: int | None = None


class PendingUser(BaseModel):
    pass


class ListUsersResponse(BaseResponseModel):

    success: bool
    users: List[User]
    invites: List[InvitedUser] = []
    pending: List[PendingUser] = []
    user_groups: List[Any] = []
    site_gruops: List[Any] = []
