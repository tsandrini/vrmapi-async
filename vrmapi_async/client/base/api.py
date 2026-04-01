"""Base API namespace for VRM API client."""

from collections.abc import Callable
from typing import Any

from vrmapi_async.routes import VRMRoutes


class BaseNamespace:
    """Base class for API namespaces."""

    def __init__(self, request_method: Callable[..., Any], routes: VRMRoutes) -> None:
        """Initialize namespace with request method and routes."""
        self._request = request_method
        self.routes = routes
