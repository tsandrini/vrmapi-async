# --- vrmapi_async/models.py
"""Pydantic models for VRM API responses."""
from enum import IntEnum, Enum
from typing import List, Any, Dict, Annotated

from pydantic import Field, field_validator, Json
from vrmapi_async.client.base.schema import (
    BaseModel,
    BaseResponseModel,
    BaseUser,
    UserIdField,
)


class AlarmMonitoringLevel(IntEnum):
    none = 0
    alarms = 1
    alarms_and_warnings = 2


class User(BaseUser):
    # -- DEFINED BY DOCS --
    user_id: UserIdField
    # -- UNDOCUMENTED --
    access_token_id: int | None = Field(None, alias="idAccessToken")


class InstallationTag(BaseModel):
    # -- DEFINED BY DOCS --
    tag_id: int = Field(alias="idTag")
    name: str
    automatic: bool
    # -- UNDOCUMENTED --
    source: str


class InstallationImage(BaseModel):
    # -- DEFINED BY DOCS --
    site_image_id: int = Field(alias="idSiteImage")
    image_name: str
    url: str


class InstallationViewPermissions(BaseModel):
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
    formatted_value: str
    raw_value: InstanceRawValue | None = None
    text_value: str | None = None
    timestamp: int | None = None


class ExtendedAttributeDataType(str, Enum):
    string = "string"
    float = "float"
    enum = "enum"


class InstallationExtendedAttribute(BaseModel):
    """
    Model for an extended installation attribute.

    The main struggle of this model is that it can be nested and recursive,
    that is, a parent attribute can have child attributes, which is why
    every field is optional. Most of the attributes are required
    in the end child nodes, but the parent nodes can have basically
    all fields set to None.

    You can practically test this with `len(attribute.data_attributes) > 0`,
    and traverse from here.
    """

    # -- DEFINED BY DOCS --
    data_attribute_id: int | None = Field(None, alias="idDataAttribute")
    code: str | None = None
    description: str | None = None
    format_with_unit: str | None = None
    data_type: ExtendedAttributeDataType | None = None  # TODO create an enum
    text_value: str | None = None
    instance: int | None = None  # DOCS says this is string, but it's actually an int
    timestamp: int | None = None  # DOCS says string again
    dbus_service_type: str | None = None
    dbus_path: str | None = None
    raw_value: InstanceRawValue | None = None
    formatted_value: str | None = None
    data_attribute_enum_values: List[Dict[str, InstanceRawValue | None]] = []
    # -- UNDOCUMENTED --
    device_type_id: int | None = Field(None, alias="idDeviceType")
    instances: List[Any] | dict = []  # TODO this is broken for some reason
    consists_of_attribute_codes: List[str] = []
    data_attributes: List["InstallationExtendedAttribute"] = []


class Site(BaseModel):
    """
    Model for a VRM Site (Non-Extended).
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
    inverter_charger_control: bool

    @field_validator("phonenumber", mode="before")
    @classmethod
    def convert_phone_to_str(cls, v: Any) -> str | None:
        """Converts integer or other phonenumbers to strings if not None."""
        return None if v is None else str(v)


class SiteExtended(Site):
    """
    Model for an Extended VRM Site. Inherits from Site and allows
    extra fields, capturing the 'extended' block.
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
    current_alarms: List[dict]  # TODO
    num_alarms: int
    avatar_url: str | None = None
    tags: List[InstallationTag]
    images: List[InstallationImage]
    view_permissions: InstallationViewPermissions
    extended: List[InstallationExtendedAttribute]
    # -- UNDOCUMENTED --
    gui_v: int | None = Field(None, alias="GUIv")
    gui_hash: str | None = None
    new_tags: bool
    no_data_alarm_timeout: int | None = None
    nodered_running: bool
    prices_unavailable: bool | None = None
    remote_console_choice: str | None = None  # TODO

    @field_validator("tags", "images", mode="before")
    @classmethod
    def unify_list_or_bool_input(cls, v: List[dict] | bool) -> List[dict]:
        if isinstance(v, bool):
            return []
        return v


class UserSitesResponse(BaseResponseModel):
    """Response model for fetching non-extended user sites."""

    success: bool
    records: List[Site]


class UserSitesExtendedResponse(BaseResponseModel):
    """Response model for fetching extended user sites."""

    success: bool
    records: List[SiteExtended]


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
    # NOTE: Docs say that all of these fields are optional, they don't seem to be
    site_id: int
    site_identifier: str
    site_name: str
    avatar_url: str | None = None
    highlight: Dict[str, List[str]]


class InstallationSearchResponse(BaseResponseModel):
    success: bool
    count: int
    results: List[InstallationSearchResult]


class CreateAccessTokenResponse(BaseResponseModel):
    """Response model for creating an access token."""

    success: bool
    token: str
    access_token_id: int = Field(..., alias="idAccessToken")  # NOTE: docs says str


class UsersListAccessTokensResponse(BaseResponseModel):
    """Response model for listing user access tokens."""

    success: bool
    tokens: List[AccessToken]


# TODO: API returns a JSON returns object with a single key 'site_id' for this endpoint.
#       But this is also the most flexible way in case they add additional stuff
#       into the records object in the future.
class SiteId(BaseModel):
    site_id: int


class RevokeAccessTokenData(BaseModel):
    removed: int


class SiteIdByIdentifierResponse(BaseResponseModel):
    """
    Response model for getting a site ID by installation identifier.
    Mainly used for the records.site_id field.
    """

    success: bool
    records: SiteId


class CreateInstallationResponse(BaseResponseModel):
    """
    Response model for creating a new installation.
    Contains the created Site object.
    """

    success: bool
    records: SiteId


class AboutMeResponse(BaseResponseModel):
    """
    Response model for the 'about me' endpoint that returns information
    about the currently authenticated user.
    """

    success: bool
    user: User


class RevokeAccessTokenResponse(BaseResponseModel):
    """
    Response model for revoking an access token.
    Contains the ID of the revoked access token.
    """

    success: bool
    data: RevokeAccessTokenData
