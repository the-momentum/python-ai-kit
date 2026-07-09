from typing import Any, Callable

from app.utils.date_handlers import (
    get_current_week,
    get_today_date,
    get_weekday_from_date,
)

DATEUTILS_TOOLS: list[Callable[..., Any]] = [
    get_today_date,
    get_current_week,
    get_weekday_from_date,
]
