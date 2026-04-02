# Usage

The client is organized into **namespaces**, each corresponding
to a section of the VRM API. After connecting, access them as
attributes on the client object:

```python
async with VRMAsyncAPI(demo=True) as client:
    client.users          # UsersNamespace
    client.installations  # InstallationsNamespace
```

## Authentication

`vrmapi-async` supports three mutually exclusive authentication
modes. Exactly one must be provided when constructing the client.

### Credentials (username + password)

Logs in via `POST /auth/login` and receives a JWT token.

```python
client = VRMAsyncAPI(
    username="you@example.com", password="secret"
)
```

!!! note
    The JWT token is obtained during `connect()` and used for
    all subsequent requests. On `disconnect()`, the session is
    logged out via `POST /auth/logout`.

### Demo account

Uses the VRM demo account (user ID 22, site ID 151734).
No credentials needed.

```python
client = VRMAsyncAPI(demo=True)
```

Useful for testing and development. The demo site has
realistic data but is read-only.

### API token

Uses a pre-created access token. No login/logout calls
are made.

```python
client = VRMAsyncAPI(
    token="your-token", user_id_for_token=12345
)
```

!!! tip
    Create access tokens via the VRM portal or
    programmatically with
    [`client.users.create_access_token()`][vrmapi_async.client.users.api.UsersNamespace.create_access_token].

### Auth header

All three modes set the `X-Authorization` header:

| Mode        | Header value          |
| ----------- | --------------------- |
| Credentials | `Bearer <jwt>`        |
| Demo        | `Bearer <jwt>`        |
| Token       | `Token <access_token>`|

### Validation

The constructor raises `ValueError` if:

- No auth method is provided
- Multiple auth methods are provided
- Only `token` or only `user_id_for_token` is given
  (both required)
- Only `username` or only `password` is given
  (both required)

## Users namespace

The users namespace provides methods for user account
management, installation discovery, and access token
operations. Access it via `client.users`.

### About me

Get the current authenticated user's profile:

```python
resp = await client.users.about_me()
print(resp.user.name, resp.user.email)
```

### List installations

```python
resp = await client.users.list_installations(client.user_id)
for site in resp.records:
    print(f"{site.name} (ID: {site.id_site})")
```

#### Extended installation data

Use `list_installations_extended()` to get additional device
and attribute information:

```python
resp = await client.users.list_installations_extended(
    client.user_id
)
for site in resp.records:
    print(site.name, site.extended)
```

### Search installations

Search by name, identifier, or other fields:

```python
resp = await client.users.search_installations_by_query(
    client.user_id, "my-site"
)
for site in resp.records:
    print(site.name)
```

### Get site ID by identifier

Look up a site's numeric ID from its device identifier:

```python
resp = await client.users.get_site_id_by_identifier(
    client.user_id, "abc123def456"
)
print(resp.id_site)
```

### Access tokens

#### List tokens

```python
resp = await client.users.list_access_tokens(client.user_id)
for token in resp.records:
    print(token.name, token.id_access_token)
```

#### Create a token

```python
from datetime import datetime, timezone

resp = await client.users.create_access_token(
    client.user_id,
    name="my-automation-token",
    expiry=datetime(2025, 12, 31, tzinfo=timezone.utc),
)
print(resp.token)  # save this --- you won't see it again
```

#### Revoke a token

```python
await client.users.revoke_access_token(
    client.user_id, token_id=42
)
```

## Installations namespace

The installations namespace provides methods for querying
site-level data like consumption stats and user access.
Access it via `client.installations`.

### Consumption stats

Retrieve consumption statistics for a site:

```python
resp = await client.installations.get_consumption_stats(
    site_id=151734
)
for record in resp.records:
    print(record)
```

#### With date range

Pass `start` and `end` as `datetime` objects to limit the
time range. They are automatically converted to UNIX epoch
timestamps:

```python
from datetime import datetime, timezone

resp = await client.installations.get_consumption_stats(
    site_id=151734,
    start=datetime(2024, 1, 1, tzinfo=timezone.utc),
    end=datetime(2024, 1, 31, tzinfo=timezone.utc),
)
```

### List site users

Get all users that have access to an installation:

```python
resp = await client.installations.list_users(site_id=151734)
for user in resp.records:
    print(user.name, user.email)
```

## Error handling

### Exception hierarchy

```text
VRMAPIError (base)
├── VRMAuthenticationError   # 401/403
├── VRMAPIRequestError       # General request failures
└── VRMRateLimitError        # 429, rate limit exhausted
```

All exceptions inherit from `VRMAPIError`.
`VRMAPIRequestError` and `VRMRateLimitError` include
`status_code` and `response_text` attributes.

### Catching errors

```python
from vrmapi_async.exceptions import (
    VRMAPIError,
    VRMAPIRequestError,
    VRMAuthenticationError,
    VRMRateLimitError,
)

try:
    resp = await client.users.about_me()
except VRMAuthenticationError:
    print("Bad credentials or expired session")
except VRMRateLimitError as e:
    print(f"Rate limited after retries: {e.status_code}")
except VRMAPIRequestError as e:
    print(f"Request failed: {e.status_code}")
except VRMAPIError:
    print("Something else went wrong")
```

### Automatic retries

The client automatically retries on:

- **429 (rate limit)** --- respects the `Retry-After` header
- **5xx (transient server errors)** --- 500, 502, 503, 504
  (enabled by default)

Retries use exponential backoff:
`max(retry_after, base * 2^attempt)` seconds.

```python
client = VRMAsyncAPI(
    demo=True,
    max_retries=5,            # default: 3
    retry_backoff_base=2.0,   # default: 1.0 (seconds)
    retry_on_5xx=False,       # default: True
)
```

If all retries are exhausted, `VRMRateLimitError` (for 429)
or `VRMAPIRequestError` (for 5xx) is raised.

### Raw response access

All response models store the original JSON dict in `_raw`:

```python
resp = await client.users.about_me()

# Access undocumented or extra fields
print(resp._raw["some_undocumented_field"])
```

This is useful because the VRM API frequently returns fields
not documented in the spec.
