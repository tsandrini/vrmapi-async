from pydantic import Field
from typing import Optional

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
    verification_mode: Optional[str] = None
    verification_sent: Optional[bool] = None
    # -- UNDOCUMENTED --
    status: Optional[str] = None
