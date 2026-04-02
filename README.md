# vrmapi-async

A modern, async Python client for the
[Victron Energy VRM API](https://vrm-api-docs.victronenergy.com/).

Built on [httpx](https://www.python-httpx.org/) and
[Pydantic v2](https://docs.pydantic.dev/), `vrmapi-async`
provides a fully typed, async-first interface to the VRM
portal.

**Key features:**

- **Fully async**: built on `httpx.AsyncClient`
  with native `async with` support
- **Pydantic v2 models**: all responses are parsed into
  typed models with full IDE autocompletion
- **Three auth modes**: credentials, demo account, or
  API token
- **Automatic retries**: rate limit (429) and transient 5xx
  handling with exponential backoff
- **Raw response escape hatch**: access undocumented
  fields via `response._raw`
- **Namespace-based API**: `client.users.*`,
  `client.installations.*`

## Installation

```bash
pip install vrmapi-async
```

**Requirements:** Python 3.10+,
[httpx](https://www.python-httpx.org/) >= 0.27.0,
[Pydantic](https://docs.pydantic.dev/) >= 2.7.0

## Quick start

```python
import asyncio
from vrmapi_async import VRMAsyncAPI

async def main():
    async with VRMAsyncAPI(demo=True) as client:
        me = await client.users.about_me()
        print(f"Logged in as: {me.user.name}")

        installations = await client.users.list_installations(
            client.user_id
        )
        for site in installations.records:
            print(f"  Site: {site.name} (ID: {site.id_site})")

asyncio.run(main())
```

### Authentication modes

```python
# 1. Username + password
async with VRMAsyncAPI(
    username="you@example.com", password="secret"
) as client:
    ...

# 2. API access token
async with VRMAsyncAPI(
    token="your-token", user_id_for_token=12345
) as client:
    ...

# 3. Demo account (for testing)
async with VRMAsyncAPI(demo=True) as client:
    ...
```

## Documentation

Full documentation is available at
<https://tsandrini.github.io/vrmapi-async/>.

## License

EUPL-1.2
