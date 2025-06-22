from typing import Annotated

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, AliasChoices, Field
from vrmapi_async.utils import snake_case_to_camel_case

UserIdField = Annotated[
    int, Field(validation_alias=AliasChoices("user_id", "id_user", "idUser", "userId"))
]


class BaseTemplateModel(PydanticBaseModel):
    """
    Base model for all VRM API schemas.
    Mainly used to override global configuration settings.
    """

    model_config = ConfigDict(
        alias_generator=lambda field_name: snake_case_to_camel_case(field_name),
        extra="allow",  # TODO change in prod
        validate_by_name=True,
    )


class BaseModel(BaseTemplateModel):
    """
    Base model for all VRM API schemas.
    Inherits from BaseTemplateModel to apply global configuration.
    """

    pass


class BaseResponseModel(BaseTemplateModel):
    """
    Base model for all VRM API response schemas.
    Inherits from BaseTemplateModel to apply global configuration.
    """

    pass


class BaseUser(BaseModel):
    """
    Base model for user-related schemas.

    VRM API isn't unfortunately very consistent with its API, so the child
    classes with have to rename and override certain fields.
    """

    user_id: UserIdField
    name: str
    email: str
    country: str | None = None
    avatar_url: str | None = None
