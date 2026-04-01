"""Shared test fixtures for vrmapi-async tests."""

import pytest
import respx

from vrmapi_async.client import VRMAsyncAPI


# Marker registration
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "online: hits the real VRM demo API (deselect with -m 'not online')"
    )


@pytest.fixture()
def mock_api(respx_mock: respx.MockRouter):
    """Return a token-authed VRMAsyncAPI with respx intercepting all HTTP.

    The client is pre-authenticated (token mode skips network on connect()),
    so tests can call namespace methods immediately after ``await client.connect()``.
    """
    return VRMAsyncAPI(
        token="fake-token-for-tests",
        user_id_for_token=42,
        max_retries=0,
    )


@pytest.fixture()
def mock_api_with_retries(respx_mock: respx.MockRouter):
    """Create a mock API client with retries enabled for testing retry logic."""
    return VRMAsyncAPI(
        token="fake-token-for-tests",
        user_id_for_token=42,
        max_retries=3,
        retry_backoff_base=0.0,  # No actual delay in tests
    )
