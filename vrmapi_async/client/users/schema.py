# --- vrmapi_async/models.py
"""Pydantic models for VRM API responses."""

from pydantic import Field, ConfigDict, field_validator, Json
from typing import List, Optional, Any, Dict

from vrmapi_async.client.base.schema import BaseModel, BaseResponseModel


class User(BaseModel):

    # -- DEFINED BY DOCS --
    user_id: int = Field(..., alias="id")
    name: str
    email: str
    country: str
    # -- UNDOCUMENTED --
    id_access_token: Optional[int] = Field(None, alias="idAccessToken")


class Site(BaseModel):
    """
    Model for a VRM Site (Non-Extended).
    Strictly defines fields expected in the non-extended response.
    """

    # -- DEFINED BY DOCS --
    id_site: int = Field(..., alias="idSite")
    access_level: int = Field(..., alias="accessLevel")
    owner: bool
    is_admin: bool
    name: str
    identifier: str
    id_user: int = Field(..., alias="idUser")
    pv_max: int = Field(..., alias="pvMax")
    timezone: str
    phonenumber: Optional[str] = None
    notes: Optional[str] = None
    geofence: Optional[Json[Any]] = None
    geofence_enabled: bool = Field(..., alias="geofenceEnabled")
    realtime_updates: bool = Field(..., alias="realtimeUpdates")
    has_mains: bool = Field(..., alias="hasMains")
    has_generator: bool = Field(..., alias="hasGenerator")
    no_data_alarm_timeout: Optional[int] = Field(None, alias="noDataAlarmTimeout")
    alarm_monitoring: int = Field(..., alias="alarmMonitoring")
    invalid_vrm_auth_token_used_in_log_request: bool = Field(
        ..., alias="invalidVRMAuthTokenUsedInLogRequest"
    )
    syscreated: int
    shared: bool
    device_icon: Optional[str] = Field(None, alias="device_icon")
    # -- UNDOCUMENTED --
    is_paygo: Optional[bool] = Field(..., alias="isPaygo")
    paygo_currency: Optional[str] = Field(None, alias="paygoCurrency")
    paygo_total_amount: Optional[float] = Field(None, alias="paygoTotalAmount")
    id_currency: Optional[int] = Field(None, alias="idCurrency")
    currency_code: Optional[str] = Field(None, alias="currencyCode")
    currency_sign: Optional[str] = Field(None, alias="currencySign")
    currency_name: Optional[str] = Field(None, alias="currencyName")
    inverter_charger_control: Optional[bool] = Field(
        ..., alias="inverterChargerControl"
    )

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @field_validator("phonenumber", mode="before")
    @classmethod
    def convert_phone_to_str(cls, v: Any) -> Optional[str]:
        """Converts integer or other phonenumbers to strings if not None."""
        if v is None:
            return None
        return str(v)


class SiteExtended(Site):
    """
    Model for an Extended VRM Site. Inherits from Site and allows
    extra fields, capturing the 'extended' block.
    """

    # tags: Optional[List[Dict[str, Any]]] = None
    # extended: Optional[Dict[str, Any]] = None
    # Add any other specific top-level fields from extended you want to model
    # alarm: Optional[int] = None
    alarm: Optional[bool] = None
    last_timestamp: Optional[int] = None
    current_time: Optional[str] = None
    timezone_offset: Optional[int] = None
    demo_mode: Optional[bool] = None
    mqtt_webhost: Optional[str] = None
    mqtt_host: Optional[str] = None
    high_workload: Optional[bool] = None
    current_alarms: Optional[List[dict]] = None

    # Allow extra fields for the extended model
    model_config = ConfigDict(extra="allow", populate_by_name=True)


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
    id_access_token: int = Field(..., alias="idAccessToken")  # NOTE: docs says str
    name: str
    created_on: int = Field(..., alias="createdOn")
    scope: str
    expires: Optional[int] = None
    # -- UNDOCUMENTED --
    last_seen: Optional[int] = Field(None, alias="lastSeen")
    last_successful_auth: Optional[int] = Field(None, alias="lastSuccessfulAuth")


class InstallationSearchResult(BaseModel):
    # NOTE: Docs say that all of these fields are optional, they don't seem to be
    site_id: int
    site_identifier: str
    site_name: str
    avatar_url: Optional[str] = None
    highlight: Dict[str, List[str]]


class InstallationSearchResponse(BaseResponseModel):
    success: bool
    count: int
    results: List[InstallationSearchResult]


class CreateAccessTokenResponse(BaseResponseModel):
    """Response model for creating an access token."""

    success: bool
    token: str
    id_access_token: int = Field(..., alias="idAccessToken")  # NOTE: docs says str


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
