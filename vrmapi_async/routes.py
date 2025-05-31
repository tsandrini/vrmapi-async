from dataclasses import dataclass


@dataclass(frozen=True)
class VRMRoutes:
    """Holds all VRM API endpoint path templates."""

    AUTH_LOGIN: str = "/auth/login"
    AUTH_LOGOUT: str = "/auth/logout"
    AUTH_DEMO: str = "/auth/loginAsDemo"

    USERS_ABOUTME: str = "/users/me"
    USERS_INSTALLATIONS_LIST: str = "/users/{user_id}/installations"
    USERS_INSTALLATIONS_SEARCH: str = "/users/{user_id}/search"
    USERS_INSTALLATIONS_ID_BY_IDENTIFIER: str = "/users/{user_id}/get-site-id"
    USERS_INSTALLATIONS_CREATE: str = "/users/{user_id}/addsite"
    USERS_ACCESSTOKENS_LIST: str = "/users/{user_id}/accesstokens/list"
    USERS_ACCESSTOKENS_CREATE: str = "/users/{user_id}/accesstokens/create"
    USERS_ACCESSTOKENS_REVOKE: str = (
        "/users/{user_id}/accesstokens/{access_token_id}/revoke"
    )

    INSTALLATIONS_STATS: str = "/installations/{site_id}/stats"
    INSTALLATIONS_OVERALL_STATS: str = "/installations/{site_id}/overallstats"
    INSTALLATIONS_DIAGNOSTICS: str = "/installations/{site_id}/diagnostics"
    INSTALLATIONS_USERS_LIST: str = "/installations/{site_id}/users"

    INSTALLATIONS_WIDGETS: str = "/installations/{site_id}/widgets/{widget_type}"
