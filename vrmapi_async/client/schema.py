from pydantic import Field

from vrmapi_async.client.base.schema import BaseResponseModel


class LoginResponse(BaseResponseModel):
    """Response model for successful login."""

    # -- DEFINED BY VRMAPI DOCS --
    token: str
    user_id: int = Field(..., alias="idUser")
    verification_mode: str
    verification_sent: bool
    # -- UNDOCUMENTED --
    status: str


class DemoLoginResponse(BaseResponseModel):
    """Response model for demo login."""

    # -- DEFINED BY VRMAPI DOCS --
    token: str
    user_id: int = Field(..., alias="idUser")
    verification_mode: str | None = None
    verification_sent: bool | None = None
    # -- UNDOCUMENTED --
    status: str | None = None
