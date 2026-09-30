from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import StrEnum
from os import environ
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

from clockify.errors import ConfigurationError
from clockify.errors import MissingCredentialsError
from clockify.retry import RetryPolicy

if TYPE_CHECKING:
    from collections.abc import Callable

API_KEY_ENV_VAR: Final = "CLOCKIFY_API_KEY"
# The value is an environment variable name, not a secret.
ADDON_TOKEN_ENV_VAR: Final = "CLOCKIFY_ADDON_TOKEN"  # ruff: ignore[hardcoded-password-string]

# A caller-supplied callback invoked lazily on every request instead of a fixed string,
# so a rotating or externally-managed key never has to be baked into the client at
# construction time. The SDK never calls this itself outside the auth flow.
type ApiKeyProvider = Callable[[], str]  # pylint: disable=gajaguar-module-const-naming
# Same contract as ApiKeyProvider, for the add-on token.
type AddonTokenProvider = Callable[[], str]  # pylint: disable=gajaguar-module-const-naming


class Region(StrEnum):
    GLOBAL = "GLOBAL"
    EU_CENTRAL_1 = "EU_CENTRAL_1"
    US_EAST_2 = "US_EAST_2"
    EU_WEST_2 = "EU_WEST_2"
    AP_SOUTHEAST_2 = "AP_SOUTHEAST_2"
    DEVELOPER = "DEVELOPER"


# Best-effort host strings transcribed from the public Clockify docs. They are not
# verified against a live account for every region and MUST be re-verified before a
# real release; callers can always bypass them with an explicit base_url.
# The developer sandbox exposes no separate reports host, so the same URL is reused.
_REGION_HOSTS: Final[dict[Region, tuple[str, str]]] = {
    Region.GLOBAL: ("https://api.clockify.me/api/v1", "https://reports.api.clockify.me/v1"),
    Region.EU_CENTRAL_1: ("https://euc1.clockify.me/api/v1", "https://euc1.clockify.me/report/v1"),
    Region.US_EAST_2: ("https://use2.clockify.me/api/v1", "https://use2.clockify.me/report/v1"),
    Region.EU_WEST_2: ("https://euw2.clockify.me/api/v1", "https://euw2.clockify.me/report/v1"),
    Region.AP_SOUTHEAST_2: ("https://apse2.clockify.me/api/v1", "https://apse2.clockify.me/report/v1"),
    Region.DEVELOPER: ("https://developer.clockify.me/api/v1", "https://developer.clockify.me/api/v1"),
}


@dataclass(frozen=True, slots=True, kw_only=True)
class ClientConfig:
    # repr=False: a dataclass repr would otherwise print the raw key or token into any
    # traceback or log line that captures this object.
    api_key: str | ApiKeyProvider | None = field(default=None, repr=False)
    addon_token: str | AddonTokenProvider | None = field(default=None, repr=False)
    base_url: str
    reports_base_url: str
    timeout: float = 30.0
    page_size: int = 200
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    user_agent: str = "clockify-unofficial-sdk"


@dataclass(frozen=True, slots=True)
class ClientOptions:
    region: Region = Region.GLOBAL
    base_url: str | None = None
    reports_base_url: str | None = None
    timeout: float = 30.0
    retry: RetryPolicy | None = None
    event_hooks: dict[str, list[Callable[..., Any]]] | None = None


def resolve_api_key(explicit: str | ApiKeyProvider | None) -> str | ApiKeyProvider:
    # A provider is returned as-is; it is only invoked later, per request, by ApiKeyAuth.
    if callable(explicit):
        return explicit
    if explicit:
        return explicit
    from_env = environ.get(API_KEY_ENV_VAR)
    if from_env:
        return from_env
    message = (
        f"No API key provided. Pass api_key=... or set the {API_KEY_ENV_VAR} environment variable. "
        "Create one under Profile settings > Advanced > Manage API keys."
    )
    raise MissingCredentialsError(message)


def resolve_addon_token(explicit: str | AddonTokenProvider | None) -> str | AddonTokenProvider:
    # A provider is returned as-is; it is only invoked later, per request, by AddonTokenAuth.
    if explicit:
        return explicit
    from_env = environ.get(ADDON_TOKEN_ENV_VAR)
    if from_env:
        return from_env
    message = (
        f"No add-on token provided. Pass addon_token=... or set the {ADDON_TOKEN_ENV_VAR} environment variable. "
        "Clockify issues the token to an add-on when it is installed in a workspace."
    )
    raise MissingCredentialsError(message)


def resolve_credentials(
    api_key: str | ApiKeyProvider | None, addon_token: str | AddonTokenProvider | None
) -> tuple[str | ApiKeyProvider | None, str | AddonTokenProvider | None]:
    # Exactly one of the two is returned non-None. An explicit credential beats the other
    # credential's environment variable; two explicit ones, or two environment variables
    # with nothing explicit, are ambiguous and rejected.
    if api_key and addon_token:
        message = "Pass either api_key or addon_token, not both."
        raise ConfigurationError(message)
    if addon_token:
        return None, resolve_addon_token(addon_token)
    if api_key:
        return resolve_api_key(api_key), None
    if environ.get(API_KEY_ENV_VAR) and environ.get(ADDON_TOKEN_ENV_VAR):
        message = f"Both {API_KEY_ENV_VAR} and {ADDON_TOKEN_ENV_VAR} are set; set only one."
        raise ConfigurationError(message)
    if environ.get(ADDON_TOKEN_ENV_VAR):
        return None, resolve_addon_token(None)
    return resolve_api_key(None), None


def resolve_urls(region: Region, base_url: str | None, reports_base_url: str | None) -> tuple[str, str]:
    region_base, region_reports = _REGION_HOSTS[region]
    # An explicit base_url wins outright. reports_base_url is resolved independently so a
    # caller pointing only the core API at a fake server still gets a usable reports host.
    resolved_base = base_url if base_url is not None else region_base
    resolved_reports = reports_base_url if reports_base_url is not None else region_reports
    return resolved_base, resolved_reports
