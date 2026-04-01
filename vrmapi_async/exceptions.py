"""Custom exceptions for the VRM API client."""


class VRMAPIError(Exception):
    """Base exception class for VRM API errors."""


class VRMAuthenticationError(VRMAPIError):
    """Raised when authentication fails."""


class VRMAPIRequestError(VRMAPIError):
    """Raised when an API request fails for reasons other than auth."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_text: str | None = None,
    ) -> None:
        """Initialize with message, optional status code and response text."""
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self) -> str:
        """Return a formatted error string with status code and response."""
        parts = [super().__str__()]
        if self.status_code:
            parts.append(f"Status Code: {self.status_code}")
        if self.response_text:
            parts.append(f"Response: {self.response_text}")
        return " - ".join(parts)


class VRMRateLimitError(VRMAPIRequestError):
    """Raised when rate limit is exceeded and all retries are exhausted."""
