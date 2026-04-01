"""Base Pydantic models for VRM API schemas."""

from typing import Annotated, Any, Generic, TypeVar

from pydantic import AliasChoices, ConfigDict, Field, PrivateAttr
from pydantic import BaseModel as PydanticBaseModel

from vrmapi_async.utils import snake_case_to_camel_case

T = TypeVar("T")

UserIdField = Annotated[
    int,
    Field(validation_alias=AliasChoices("user_id", "id_user", "idUser", "userId")),
]


class BaseTemplateModel(PydanticBaseModel):
    """Base model for all VRM API schemas.

    Mainly used to override global configuration settings.
    """

    model_config = ConfigDict(
        alias_generator=snake_case_to_camel_case,
        extra="ignore",
        validate_by_name=True,
    )


class BaseModel(BaseTemplateModel):
    """Base model for all VRM API schemas.

    Inherits from BaseTemplateModel to apply global configuration.
    """


class BaseResponseModel(BaseTemplateModel):
    """Base model for all VRM API response schemas.

    Captures the raw response dict in ``_raw`` so callers can access
    undocumented or unexpected fields that Pydantic would otherwise drop.
    """

    _raw: dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(self, **data: Any) -> None:
        """Initialize and capture raw response data."""
        super().__init__(**data)
        self._raw = data


class RecordsListResponse(BaseResponseModel, Generic[T]):
    """Generic response for endpoints returning ``success`` + ``records: list[T]``.

    Covers the most common VRM API pattern where the payload key is
    literally ``records`` and the value is a JSON array.
    """

    success: bool
    records: list[T] = []


class RecordsSingleResponse(BaseResponseModel, Generic[T]):
    """Generic response for endpoints returning ``success`` + ``records: T``.

    Used when the ``records`` key holds a single object rather than a list.
    """

    success: bool
    records: T


class PaginatedRecordsResponse(RecordsListResponse[T]):
    """Generic response for paginated list endpoints.

    Extends :class:`RecordsListResponse` with a ``num_records`` total count.
    """

    num_records: int


class BaseUser(BaseModel):
    """Base model for user-related schemas.

    VRM API isn't unfortunately very consistent with its API, so the child
    classes with have to rename and override certain fields.
    """

    user_id: UserIdField
    name: str
    email: str
    country: str | None = None
    avatar_url: str | None = None
