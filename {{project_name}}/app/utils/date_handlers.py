from datetime import date, datetime, timedelta
from typing import Annotated

import dateutil.parser as dparser


def get_today_date() -> str:
    return date.today().strftime("%m/%d/%Y")


def get_current_week() -> str:
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return f"This week starts at {start} and ends on {end}"


def get_weekday_from_date(
    date_to_convert: Annotated[str, "Date to establish a weekday for"],
) -> str:
    parsing_output = handle_llm_date(date_to_convert)
    if isinstance(date_to_convert, datetime):
        parsing_output = parsing_output.strftime("%A")
    return str(parsing_output)


def handle_llm_date(input_date: str) -> datetime | str:
    try:
        return dparser.parse(input_date, fuzzy=True)
    except ValueError as e:
        return "The date is not of correct format - " + str(e)
