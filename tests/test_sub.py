import uuid
from datetime import date, datetime, timezone

import mock
import pytest
from dateutil.relativedelta import relativedelta

import freezegun
from yamlscript import ExpressionGlobals, sub


class CustomGlobals(ExpressionGlobals):

    @staticmethod
    def my_func(i): return i*2


MOCK_NOW = datetime.utcnow()
MOCK_TODAY = MOCK_NOW.date()
MOCK_UUID = str(uuid.uuid4())
MOCK_STRIPPED_UUID = MOCK_UUID.replace("-", "")


@pytest.mark.parametrize(
    "name,string,expected", [

        # strings
        ("empty string",                        "",                             ""),
        ("no vars or expressions",              "some string",                  "some string"),
        ("dollar amount",                       "$200",                         "$200"),
        ("dollar amount with decimals",         "$200.50",                      "$200.50"),
        ("only char",                           "$",                            "$"),
        ("last char",                           "something$",                   "something$"),
        ("in string",                           "some$thing",                   "some$thing"),

        # variables
        ("empty var",                           "${}",                          ""),
        ("top level var",                       "${my_name}",                   "James"),
        ("nested var",                          "${my.name}",                   "David"),
        ("list item var",                       "${names.1.name}",              "David"),

        # invalid variables
        ("unclosed variable",                   "${my.name",                    ValueError),
        ("unclosed nested variable",            "${obj.${my_key}.string",       ValueError),
        ("unclosed nested variable",            "${obj.${my_key.string}",       ValueError),

        # escaped variable
        ("escaped empty var",                   "\\${}",                        "${}"),
        ("escaped top level var",               "\\${my_name}",                 "${my_name}"),
        ("escaped nested var",                  "\\${my.name}",                 "${my.name}"),
        ("escaped list item var",               "\\${names.1.name}",            "${names.1.name}"),
        ("escaped var with nested var",         "\\${names.1.${my_key}}",       "${names.1.name}"),
        ("escaped var with escaped var",        "\\${names.1.\\${my_key}}",     "${names.1.${my_key}}"),

        # expressions
        ("empty expression",                    "$()",                          ""),
        ("expression with string var",          "$('${my.name}')",              "David"),
        ("expression with string concat var",   "$('name: ' + '${my.name}')",   "name: David"),
        ("custom g function",                   "$(my_func(10))",               20),
        ("custom g function to string",         "$(str(my_func(10)))",          "20"),
        ("custom g function with var param",    "$(my_func(${my_int}))",        20),

        # invalid expressions
        ("unclosed expression",                 "$(1 + 2",                      ValueError),
        ("nested unclosed variable",            "$('name' + ${my_key)",         ValueError),
        ("unclosed nested variable",            "$('name' + ${my_key}",         ValueError),

        # escaped expressions
        ("escaped empty expression",            "\\$()",                        "$()"),
        ("escaped expression with var",         "\\$(10 + ${my_int})",          "$(10 + 10)"),
        ("escaped expression with escaped var", "\\$(10 + \\${my_int})",        "$(10 + ${my_int})"),

        # methods
        ("now",                                 "$(now())",                     MOCK_NOW),
        ("today",                               "$(today())",                   MOCK_TODAY),
        ("date from string",                    "$(date('1970-01-01'))",        date(year=1970, month=1, day=1)),

        ("date from parts",                     "$(date(year=1970, month=1, day=1))",
                                                date(year=1970, month=1, day=1)),

        ("datetime from string",                "$(datetime('1970-01-01T00:00:00.000+00:00'))",
                                                datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)),

        ("datetime from parts",                 "$(datetime(year=1970, month=1, day=1, "
                                                "           hour=0, minute=0, second=0, "
                                                "           microsecond=0, utc_offset=0))",
                                                datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)),

        ("years",                               "$(years(${my_int}))",          relativedelta(years=10)),
        ("months",                              "$(months(${my_int}))",         relativedelta(months=10)),
        ("weeks",                               "$(weeks(${my_int}))",          relativedelta(weeks=10)),
        ("days",                                "$(days(${my_int}))",           relativedelta(days=10)),
        ("hours",                               "$(hours(${my_int}))",          relativedelta(hours=10)),
        ("minutes",                             "$(minutes(${my_int}))",        relativedelta(minutes=10)),
        ("seconds",                             "$(seconds(${my_int}))",        relativedelta(seconds=10)),
        ("microseconds",                        "$(microseconds(${my_int}))",   relativedelta(microseconds=10)),
        ("enumerate",                           "$(enumerate(${names}))",       [[0, {'name': 'James'}], [1, {'name': 'David'}]]),
        ("map",                                 "$(map(my_func, ${ints}))",     [0, 2, 4, 6]),
        ("map",                                 "$(filter("
                                                "   lambda i: i > 1, ${ints}"
                                                "))",                           [2, 3]),
        ("sum",                                 "$(sum(${ints}))",              6),
        ("min",                                 "$(min(${ints}))",              0),
        ("max",                                 "$(max(${ints}))",              3),
        ("uuid",                                "$(uuid())",                    MOCK_UUID),
        ("stripped uuid",                       "$(uuid(strip=True))",          MOCK_STRIPPED_UUID),
        ("nested exp",                          "$($(my_func(10) - 10))",       10),

        ("generated list",                      "$(["
                                                "   i['${my_key}']"
                                                "   for i in ${names}"
                                                "])",
                                                ["James", "David"]),

        ("unhandled value in list",             ["${names.0.name}", "${names.1.name}", 123],
                                                ["James", "David", 123]),

        ("variables in list",                   ["${names.0.name}", "${names.1.name}"],
                                                ["James", "David"]),

        ("generated and enumerated object",     "$({"
                                                "   item['${my_key}']: my_func(${my_int} + index)"
                                                "   for index, item in enumerate(${names})"
                                                "})",
                                                {"James": 20, "David": 22}),

        ("variables in object",                 {"a": "${names.0.name}", "b": "${names.1.name}"},
                                                {"a": "James", "b": "David"}),

        ("unhandled in object",                 {"a": "${names.0.name}", "b": "${names.1.name}", "c": 123},
                                                {"a": "James", "b": "David", "c": 123}),

        ("Two expressions",                     "$('${names.0.name}')-${names.1.name}-$(my_func(${my_int}))",
                                                "James-David-20")
    ]
)
@pytest.mark.parametrize("g", [CustomGlobals, {k: getattr(CustomGlobals, k) for k in dir(CustomGlobals)}])
@mock.patch("yamlscript.globals.uuid4", lambda: MOCK_UUID)
@freezegun.freeze_time(MOCK_NOW)
def test_sub(name, string, expected, g, context):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            sub(string, context, g=g)
    else:
        output = sub(string, context, g=g)
        assert output == expected, f"{name} : {output} != {expected}"
