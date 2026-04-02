## 0.1.0 (2026-04-02)

### Feat

- **client/installations**: remove warning for list_users endpoint
- **client/users**: add missing fields to /users/me endpoint
- **client/installations**: properly implement get_stats
- **client/base**: setup a generic RecordsListResponse
- **client**: add timeout parameter
- **client**: add rate-limiting
- **client/base/schema**: switch to a __raw dict + ignore strategy
- **flake**: update hooks & flake inputs
- **LICENSE**: move to EUPL 1.2
- **pre-commit-hooks**: add mypy hook and fix ruff entry
- **client/users**: add extended attributes to list_installations
- **client/users**: refine users schema
- **utils**: init kebab & snake case utils
- **client/users**: finalize all of the users endpoints in VRM
- **LICENSE**: move to LGPLv2
- **vrmapi_async**: init project

### Fix

- **client/users**: fix revoke_access_token method
- **client/users**: fix params= to json_data= in key user requests

### Refactor

- **shells**: cleanup defaults from flake-parts-builder
- **client**: unify user_id usage
- **.gitignore**: cleanup old irrelevant entries
- **README**: remove old README_1.md
