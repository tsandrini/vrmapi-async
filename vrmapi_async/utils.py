"""Utility functions for the VRM API client."""

import re
import math
from datetime import datetime, timezone


def datetime_to_epoch(dt: datetime) -> int:
    """
    Converts a Python datetime object to an epoch timestamp (integer seconds).

    Ensures the datetime is timezone-aware (UTC) before conversion if naive.
    Rounds up to the nearest second to match the original implementation's behavior.

    :params dt: The datetime object to convert.
    :returns: The epoch timestamp as an integer.
    """
    if dt.tzinfo is None:
        # If naive, assume it's in the system's local timezone and convert to UTC
        # Or, for consistency, always assume UTC if naive:
        dt = dt.replace(tzinfo=timezone.utc)

    # Use timestamp() which returns seconds since epoch as a float, then ceil and int
    return int(math.ceil(dt.timestamp()))


def to_snake_case(s: str) -> str:
    """
    Convert a string from various casings (CamelCase, PascalCase, kebab-case, space-separated)
    to snake_case.

    Handles acronyms as well (e.g., "HTTPRequest" -> "http_request").

    :param s: The input string to convert.
    :returns: The converted string in snake_case.
    """
    if not s:
        return ""

    s = re.sub(r"[-\s]+", "_", s.strip())
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = s.lower()
    s = re.sub(r"_+", "_", s)
    s = s.strip("_")

    return s


def snake_case_to_camel_case(snake_str: str) -> str:
    """
    Assuming a snake_case input string, this function converts it to camelCase.

    :param snake_str: The input string in snake_case.
    :returns: The converted string in camelCase.
    """
    if not snake_str:
        return ""
    components = snake_str.split("_")
    if len(components) == 1:
        return components[0]
    return components[0] + "".join(x.title() for x in components[1:])
