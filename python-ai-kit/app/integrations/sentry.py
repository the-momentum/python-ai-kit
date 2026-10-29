"""Filter credential-bearing telemetry locally before Sentry serialises or sends it"""

import re
from typing import cast

import sentry_sdk
from sentry_sdk.integrations.argv import ArgvIntegration
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber
from sentry_sdk.types import Breadcrumb, BreadcrumbHint, Event, Hint

from app.config import settings

_FILTERED = "[Filtered]"
_SENSITIVE_KEYS = frozenset(
    re.sub(r"[^a-z0-9]", "", key.lower())
    for key in [
        *DEFAULT_DENYLIST,
        "argv",
        "sys.argv",
        "command_line",
        "process.args",
        "process.command_line",
    ]
)
_SENSITIVE_SUFFIXES = (
    "password",
    "passwd",
    "secret",
    "token",
    "apikey",
    "credentials",
    "secretkey",
    "secretaccesskey",
    "masterkey",
)
_URL_USERINFO = re.compile(
    r"""(?<![a-z0-9+.-])([a-z][a-z0-9+.-]*://)(?:[^/\s?#"'<>]*@|:[^\s"'<>]*@)""",
    re.IGNORECASE,
)
_BEARER_TOKEN = re.compile(r"\bBearer\s+[a-z0-9._~+/\-]+=*", re.IGNORECASE)
_QUOTED_VALUE = r"""(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')"""
_AUTH_HEADER_CREDENTIALS = re.compile(
    rf"""(\bauthorization["']?\s*[:=]\s*)
        (?:{_QUOTED_VALUE}(?=$|[\s,;}}\]])
           |\[(?:{_QUOTED_VALUE}|[^\[\]"'])*\](?=$|[\s,;}}\]])
           |.*$)""",
    re.IGNORECASE | re.VERBOSE | re.DOTALL,
)
_SECRET_NAMES = (
    r"(?:password|passwd|secret|token|api[_-]?key|credentials|authorization"
    r"|secret[_-]?key|secret[_-]?access[_-]?key|master[_-]?key)"
)
_SECRET_ASSIGNMENT = re.compile(
    rf"""(?P<prefix>(?<![\w-])(?:
            --?[a-z0-9_-]*{_SECRET_NAMES}["']?\s+
            |[a-z0-9_-]*{_SECRET_NAMES}["']?\s*[:=]\s*
        ))
        (?:\[Filtered\]|{_QUOTED_VALUE}(?=$|[\s,;&}}\]])|["'].*$|[^\s,;&'"}}\]]+)""",
    re.IGNORECASE | re.VERBOSE | re.DOTALL,
)


def init_sentry() -> None:
    """Initialise enabled reporting without process arguments or credential-bearing data"""
    if settings.SENTRY_ENABLED:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENV,
            include_local_variables=False,
            send_default_pii=False,
            traces_sample_rate=settings.SENTRY_SAMPLES_RATE,
            disabled_integrations=[ArgvIntegration()],
            event_scrubber=_CredentialScrubber(recursive=True),
            before_send=sanitize_sentry_event,
            before_send_transaction=sanitize_sentry_event,
            before_breadcrumb=sanitize_sentry_breadcrumb,
        )


def sanitize_sentry_breadcrumb(breadcrumb: Breadcrumb, hint: BreadcrumbHint) -> Breadcrumb:
    """Mask credentials before retaining a breadcrumb on the current scope"""
    del hint
    return cast(Breadcrumb, _sanitize_value(breadcrumb))


def sanitize_sentry_event(event: Event, hint: Hint) -> Event:
    """Mask credential-bearing fields and text after SDK enrichment and serialisation"""
    del hint
    return cast(Event, _sanitize_value(event))


class _CredentialScrubber(EventScrubber):
    """Scrub before SDK truncation can turn a URL into a partial credential"""

    def scrub_event(self, event: Event) -> None:
        """Mask raw event data before default SDK scrubbing and serialisation"""
        sanitized = cast(Event, _sanitize_value(event))
        event.clear()
        event.update(sanitized)
        super().scrub_event(event)


def _is_sensitive_key(key: str) -> bool:
    """Recognise normalised secret names without changing unrelated SDK schema keys"""
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return normalized in _SENSITIVE_KEYS or normalized.endswith(_SENSITIVE_SUFFIXES)


def _sanitize_text(value: str) -> str:
    """Filter credential-bearing text and preserve reliable quoted/list value boundaries"""
    value = _URL_USERINFO.sub(rf"\1{_FILTERED}@", value)
    # Without a reliable quoted/list boundary, the remaining authorization text is sensitive.
    value = _AUTH_HEADER_CREDENTIALS.sub(rf"\1{_FILTERED}", value)
    value = _BEARER_TOKEN.sub(f"Bearer {_FILTERED}", value)
    return _SECRET_ASSIGNMENT.sub(lambda match: f"{match['prefix']}{_FILTERED}", value)


def _sanitize_value(value: object, *, depth: int = 0) -> object:
    """Copy nested telemetry with sensitive values masked and recursion bounded"""
    # Raw breadcrumbs can be cyclic. Do not fail open or recurse without a bound.
    if depth >= 20:
        return _FILTERED
    if isinstance(value, dict):
        return {
            key: (
                _FILTERED if isinstance(key, str) and _is_sensitive_key(key) else _sanitize_value(item, depth=depth + 1)
            )
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize_value(item, depth=depth + 1) for item in value]
    if isinstance(value, str):
        return _sanitize_text(value)
    return value
