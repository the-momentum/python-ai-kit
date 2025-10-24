from enum import Enum
from typing import Any, Callable, Generator

CallableGenerator = Generator[Callable[..., Any], None, None]


class EnvironmentType(str, Enum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"
