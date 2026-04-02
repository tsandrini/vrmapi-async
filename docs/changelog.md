# Changelog

## 0.1.0 (Unreleased)

Initial release.

### Features

- Async client with three authentication modes
  (credentials, demo, token)
- Automatic retry with exponential backoff for rate
  limits (429) and transient 5xx errors
- Users namespace: `about_me`, `list_installations`,
  `list_installations_extended`,
  `search_installations_by_query`,
  `get_site_id_by_identifier`, `create_installation`,
  `list_access_tokens`, `create_access_token`,
  `revoke_access_token`
- Installations namespace: `get_consumption_stats`,
  `list_users`
- Pydantic v2 response models with raw response escape
  hatch (`_raw`)
