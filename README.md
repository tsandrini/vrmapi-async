# vrmapi-async

A modern, async Python client for the
[Victron Energy VRM API](https://vrm-api-docs.victronenergy.com/), built on
`httpx` and `pydantic v2`.

## How to use

### Installation

```bash
pip install vrmapi-async
```

### Authentication

The client supports three authentication modes:

```python
from vrmapi_async.client import VRMAsyncAPI

# 1. Username + password
async with VRMAsyncAPI(username="you@example.com", password="secret") as client:
    me = await client.users.about_me()

# 2. API access token
async with VRMAsyncAPI(token="your-token", user_id_for_token=12345) as client:
    sites = await client.users.list_installations(client.user_id)

# 3. Demo account (for testing)
async with VRMAsyncAPI(demo=True) as client:
    sites = await client.users.list_installations(client.user_id)
```

### Examples

```python
import asyncio
from vrmapi_async.client import VRMAsyncAPI

async def main():
    async with VRMAsyncAPI(demo=True) as client:
        # List installations
        installations = await client.users.list_installations(client.user_id)
        print(installations.records)

        # Get consumption stats for a site
        stats = await client.installations.get_consumption_stats(site_id=151734)
        print(stats.records)

        # List users with access to a site
        users = await client.installations.list_users(site_id=151734)
        print(users.records)

asyncio.run(main())
```

## Developer environment

This project uses [Nix](https://nixos.org/) with [direnv](https://direnv.net/)
for reproducible development environments.

```bash
# 1. Install Nix (if you don't have it)
#    https://nixos.org/download/

# 2. Enter the dev environment
cd vrmapi-async
direnv allow   # or: nix develop

# 3. Run tests
pytest tests/ -v

# 4. Run linters
pre-commit run --all-files
```
