from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Iterable, Optional, Tuple, Union
from uuid import uuid4

from dateutil.relativedelta import relativedelta


class ExpressionGlobals:

    __builtins__ = {
        "bool": str,
        "dict": dict,
        "float": str,
        "int": str,
        "list": list,
        "str": str,
    }

    @classmethod
    def days(cls, num: int) -> relativedelta:
        return relativedelta(days=num)

    @classmethod
    def datetime(
        cls,
        string: Optional[str] = None,
        *,
        year: int = 0,
        month: int = 1,
        day: int = 1,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        utc_offset: int = 0
    ) -> datetime:
        if string:
            return datetime.fromisoformat(string)
        return datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            tzinfo=timezone(timedelta(hours=utc_offset)),
        )

    @classmethod
    def date(
        cls,
        string: Optional[str] = None,
        *,
        year: int = 0,
        month: int = 1,
        day: int = 1
    ) -> date:
        if string:
            return date.fromisoformat(string)
        return date(year=year, month=month, day=day)

    @classmethod
    def enumerate(cls, iterable: Iterable[Any]) -> Iterable[Tuple[int, Any]]:
        return enumerate(iterable)

    @classmethod
    def filter(
        cls, func: Callable[[Any], Iterable[Any]], iterable: Iterable[Any]
    ) -> Iterable[Any]:
        return filter(func, iterable)

    @classmethod
    def hours(cls, num: int) -> relativedelta:
        return relativedelta(hours=num)

    @classmethod
    def map(
        cls, func: Callable[[Any], Iterable[Any]], iterable: Iterable[Any]
    ) -> Iterable[Any]:
        return map(func, iterable)

    @classmethod
    def max(cls, iterable: Iterable[Union[int, float]],) -> Union[int, float]:
        return max(iterable)

    @classmethod
    def microseconds(cls, num: int) -> relativedelta:
        return relativedelta(microseconds=num)

    @classmethod
    def min(cls, iterable: Iterable[Union[int, float]],) -> Union[int, float]:
        return min(iterable)

    @classmethod
    def minutes(cls, num: int) -> relativedelta:
        return relativedelta(minutes=num)

    @classmethod
    def months(cls, num: int) -> relativedelta:
        return relativedelta(months=num)

    @classmethod
    def now(cls) -> datetime:
        return datetime.utcnow()

    @classmethod
    def seconds(cls, num: int) -> relativedelta:
        return relativedelta(seconds=num)

    @classmethod
    def sum(cls, iterable: Iterable[Union[int, float]]) -> Union[int, float]:
        return sum(iterable)

    @classmethod
    def today(cls) -> date:
        return cls.now().date()

    @classmethod
    def uuid(cls, strip: bool = False) -> str:
        if strip:
            return str(uuid4()).replace("-", "")
        return str(uuid4())

    @classmethod
    def weeks(cls, num: int) -> relativedelta:
        return relativedelta(weeks=num)

    @classmethod
    def years(cls, num: int) -> relativedelta:
        return relativedelta(years=num)
