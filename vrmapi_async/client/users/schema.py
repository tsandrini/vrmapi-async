"""Pydantic models for user-related VRM API responses."""

from enum import Enum, IntEnum
from typing import Annotated, Any

from pydantic import AliasChoices, ConfigDict, Field, Json, field_validator

from vrmapi_async.client.base.schema import (
    BaseModel,
    BaseResponseModel,
    BaseUser,
    RecordsListResponse,
    RecordsSingleResponse,
    UserIdField,
)


class AlarmMonitoringLevel(IntEnum):
    """Alarm monitoring sensitivity levels."""

    none = 0
    alarms = 1
    alarms_and_warnings = 2


class User(BaseUser):
    """VRM user with optional access token reference."""

    # -- DEFINED BY DOCS --
    user_id: int = Field(validation_alias=AliasChoices("id", "user_id"))
    access_level: int = 0
    # -- UNDOCUMENTED --
    access_token_id: int | None = Field(None, alias="idAccessToken")


class InstallationTag(BaseModel):
    """Tag associated with a VRM installation."""

    # -- DEFINED BY DOCS --
    tag_id: int = Field(alias="idTag")
    name: str
    automatic: bool
    # -- UNDOCUMENTED --
    source: str


class InstallationImage(BaseModel):
    """Image associated with a VRM installation."""

    # -- DEFINED BY DOCS --
    site_image_id: int = Field(alias="idSiteImage")
    image_name: str
    url: str


class InstallationViewPermissions(BaseModel):
    """View permissions for a VRM installation."""

    # -- DEFINED BY DOCS --
    update_settings: bool
    settings: bool
    diagnostics: bool
    share: bool
    # vnc: bool # NOTE: this one is missing
    mqtt_rpc: bool
    vebus: bool
    twoway: bool
    exact_location: bool
    nodered: bool
    nodered_dash: bool
    signalk: bool
    # -- UNDOCUMENTED --
    can_alter_installation: bool
    can_see_group_and_team_members: bool
    dess_config: bool
    nodered_dash_v2: bool
    paygo: bool
    rc_classic: bool
    rc_gui_v2: bool
    readonly_realtime: bool


InstanceRawValue = Annotated[str | int | float, Field()]


class ExtendedAttributeInstance(BaseModel):
    """Single instance of an extended attribute value."""

    formatted_value: str
    raw_value: InstanceRawValue | None = None
    text_value: str | None = None
    timestamp: int | None = None


class ExtendedAttributeDataType(str, Enum):
    """Data types for extended installation attributes."""

    string = "string"
    float = "float"
    enum = "enum"


class InstallationExtendedAttribute(BaseModel):
    """Model for an extended installation attribute.

    Uses ``extra="allow"`` because the VRM API returns unpredictable and
    undocumented fields here, and the recursive/nested structure makes
    strict validation impractical.

    The main struggle of this model is that it can be nested and recursive,
    that is, a parent attribute can have child attributes, which is why
    every field is optional. Most of the attributes are required
    in the end child nodes, but the parent nodes can have basically
    all fields set to None.

    You can practically test this with ``len(attribute.data_attributes) > 0``,
    and traverse from here.
    """

    model_config = ConfigDict(extra="allow")

    # -- DEFINED BY DOCS --
    data_attribute_id: int | None = Field(None, alias="idDataAttribute")
    code: str | None = None
    description: str | None = None
    format_with_unit: str | None = None
    data_type: ExtendedAttributeDataType | None = None
    text_value: str | None = None
    instance: int | None = None
    timestamp: int | None = None
    dbus_service_type: str | None = None
    dbus_path: str | None = None
    raw_value: InstanceRawValue | None = None
    formatted_value: str | None = None
    data_attribute_enum_values: list[dict[str, InstanceRawValue | None]] = []
    # -- UNDOCUMENTED --
    device_type_id: int | None = Field(None, alias="idDeviceType")
    # TODO(tsandrini): instances field is broken for some reason
    instances: list[Any] | dict[str, Any] = []
    consists_of_attribute_codes: list[str] = []
    data_attributes: list["InstallationExtendedAttribute"] = []


class Site(BaseModel):
    """Model for a VRM Site (Non-Extended).

    Strictly defines fields expected in the non-extended response.
    """

    # -- DEFINED BY DOCS --
    site_id: int = Field(alias="idSite")
    access_level: int
    owner: bool
    is_admin: bool
    name: str
    identifier: str
    user_id: UserIdField
    pv_max: int
    timezone: str
    phonenumber: str | None = None
    notes: str | None = None
    geofence: Json[Any] | None = None
    geofence_enabled: bool
    realtime_updates: bool
    has_mains: bool
    has_generator: bool
    no_data_alarm_timeout: int | None = None
    alarm_monitoring: AlarmMonitoringLevel
    invalid_vrm_auth_token_used_in_log_request: bool = Field(
        alias="invalidVRMAuthTokenUsedInLogRequest"
    )
    syscreated: int
    shared: bool
    device_icon: str | None
    # -- UNDOCUMENTED --
    is_paygo: bool
    paygo_currency: bool | None = None
    paygo_total_amount: float | None = None
    id_currency: int | None = None
    currency_code: str | None = None
    currency_sign: str | None = None
    currency_name: str | None = None
    restrict_node_red: bool = False
    favorite: int = 0
    is_system: int = Field(0, alias="isSystem")
    inverter_charger_control: bool

    @field_validator("phonenumber", mode="before")
    @classmethod
    def convert_phone_to_str(cls, v: Any) -> str | None:
        """Convert integer or other phone numbers to strings."""
        return None if v is None else str(v)


class SiteExtended(Site):
    """Model for an Extended VRM Site.

    Inherits from Site and allows extra fields,
    capturing the 'extended' block.
    """

    # -- DEFINED BY DOCS --
    alarm: bool
    last_timestamp: int
    current_time: str
    timezone_offset: int
    demo_mode: bool
    mqtt_webhost: str
    mqtt_host: str
    high_workload: bool
    # TODO(tsandrini): type current_alarms properly
    current_alarms: list[dict[str, Any]] = []
    num_alarms: int
    avatar_url: str | None = None
    tags: list[InstallationTag] = []
    images: list[InstallationImage] = []
    view_permissions: InstallationViewPermissions
    extended: list[InstallationExtendedAttribute] = []
    # -- UNDOCUMENTED --
    gui_v: int | None = Field(None, alias="GUIv")
    gui_hash: str | None = None
    new_tags: bool
    no_data_alarm_timeout: int | None = None
    nodered_running: bool
    prices_unavailable: bool | None = None
    # TODO(tsandrini): type remote_console_choice properly
    remote_console_choice: str | None = None

    @field_validator("tags", "images", mode="before")
    @classmethod
    def unify_list_or_bool_input(
        cls, v: list[dict[str, Any]] | bool
    ) -> list[dict[str, Any]]:
        """Convert ``false`` to empty list for tags/images fields."""
        if isinstance(v, bool):
            return []
        return v


class UserSitesResponse(RecordsListResponse[Site]):
    """Response model for fetching non-extended user sites."""


class UserSitesExtendedResponse(RecordsListResponse[SiteExtended]):
    """Response model for fetching extended user sites."""


class AccessToken(BaseModel):
    """Model for an access token."""

    # -- DEFINED BY DOCS --
    access_token_id: int = Field(..., alias="idAccessToken")  # NOTE: docs says str
    name: str
    created_on: int
    scope: str
    expires: int | None = None
    # -- UNDOCUMENTED --
    last_seen: int | None = None
    last_successful_auth: int | None = None


class InstallationSearchResult(BaseModel):
    """Single result from an installation search query."""

    # NOTE: Docs say that all of these fields are optional,
    # they don't seem to be
    site_id: int
    site_identifier: str
    site_name: str
    avatar_url: str | None = None
    highlight: dict[str, list[str]]


class InstallationSearchResponse(BaseResponseModel):
    """Response model for installation search results."""

    success: bool
    count: int
    results: list[InstallationSearchResult]


class CreateAccessTokenResponse(BaseResponseModel):
    """Response model for creating an access token."""

    success: bool
    token: str
    access_token_id: int = Field(..., alias="idAccessToken")  # NOTE: docs says str


class UsersListAccessTokensResponse(BaseResponseModel):
    """Response model for listing user access tokens."""

    success: bool
    tokens: list[AccessToken] = []


# TODO(tsandrini): API returns a JSON object with a single key
# 'site_id' for this endpoint, but this is also the most flexible
# way in case they add additional stuff into the records object.
class SiteId(BaseModel):
    """Model for a site ID reference."""

    site_id: int


class RevokeAccessTokenData(BaseModel):
    """Data payload for an access token revocation response."""

    removed: int


class SiteIdByIdentifierResponse(RecordsSingleResponse[SiteId]):
    """Response model for getting a site ID by installation identifier.

    Mainly used for the records.site_id field.
    """


class CreateInstallationResponse(RecordsSingleResponse[SiteId]):
    """Response model for creating a new installation.

    Contains the created Site object.
    """


class AboutMeResponse(BaseResponseModel):
    """Response model for the 'about me' endpoint.

    Returns information about the currently authenticated user.
    """

    success: bool
    user: User


class RevokeAccessTokenResponse(BaseResponseModel):
    """Response model for revoking an access token.

    Contains the ID of the revoked access token.
    """

    success: bool
    data: RevokeAccessTokenData
