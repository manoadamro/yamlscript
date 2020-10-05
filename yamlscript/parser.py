import re
from typing import Any, Dict, Iterable, List, Mapping, Tuple, Type, Union

import jsonpointer

from . import globals

SPECIAL_CHAR = "$"
VARIABLE_SCOPE = "{}"
EXPRESSION_SCOPE = "()"
ESCAPE_CHAR = "\\"


def _finder(
    string: str, special_char: str, start_char: str, end_char: str, escape_char: str
) -> Dict[str, Any]:
    def _find_end() -> Tuple[int, str]:
        stack = 0
        for relative_index, char in enumerate(string[start + offset :]):
            index = start + relative_index + offset
            if char == start_char:
                stack += 1
            if char == end_char:
                stack -= 1
            if stack == 0:
                return index, string[start : index + 1]
        raise ValueError

    last: int = 0
    out: Dict[str, Any] = {}
    regex = (
        f"(?<!{re.escape(escape_char)})"
        + re.escape(special_char)
        + re.escape(start_char)
    )
    for start in (m.start() for m in re.finditer(regex, string)):
        if start < last:
            continue
        offset = len(special_char)
        last, sub_string = _find_end()
        out.setdefault(sub_string, sub_string[offset + 1 : -1])

    return out


def _find_expressions(string: str) -> Dict[str, Any]:
    return _finder(
        string, SPECIAL_CHAR, EXPRESSION_SCOPE[0], EXPRESSION_SCOPE[1], ESCAPE_CHAR
    )


def _find_variables(string: str) -> Dict[str, Any]:
    return _finder(
        string, SPECIAL_CHAR, VARIABLE_SCOPE[0], VARIABLE_SCOPE[1], ESCAPE_CHAR
    )


def _sub(pattern: str, value: Any, string: str) -> Any:
    if pattern != string:
        return re.sub(re.escape(pattern), str(_dump_i(value)), string)
    return _dump_i(value)


def _sub_variables(string: str, context: Dict[str, Any]) -> str:
    variables = _find_variables(string)
    for pattern, variable in variables.items():
        value = (
            ""
            if not variable
            else jsonpointer.resolve_pointer(context, "/" + variable.replace(".", "/"))
        )
        string = _sub(pattern, value, string)
    return string


def _sub_expressions(string: str, context: Dict[str, Any], g: Dict[str, Any]) -> Any:
    expressions = _find_expressions(string)
    for pattern, expression in expressions.items():
        regex = (
            f"(?<!{re.escape(ESCAPE_CHAR)})" + re.escape(SPECIAL_CHAR) + re.escape("(")
        )
        expression = re.sub(regex, "(", expression)
        expression = _sub_variables(expression, context)
        if not expression:
            value = ""
        else:
            result: List[Any] = []
            print(g.keys())
            exec(f"_result.append({expression})", g, {"_result": result})
            value = result[0]
        string = _sub(pattern, value, string)
    return string


def _sub_string(string: str, context: Dict[str, Any], g: Dict[str, Any]) -> Any:
    value = _sub_expressions(string, context, g)
    if not isinstance(value, str):
        return value
    value = _sub_variables(value, context)
    return value.replace(ESCAPE_CHAR + SPECIAL_CHAR, SPECIAL_CHAR)


def _sub_list(
    iterable: Iterable[Any], context: Dict[str, Any], g: Dict[str, Any]
) -> List[Any]:
    return [_sub_i(item, context, g) for item in iterable]


def _sub_dict(
    obj: Mapping[str, Any], context: Dict[str, Any], g: Dict[str, Any]
) -> Dict[str, Any]:
    return {key: _sub_i(value, context, g) for key, value in obj.items()}


def _sub_i(item: Any, context: Dict[str, Any], g: Dict[str, Any]) -> Any:
    if isinstance(item, str):
        return _sub_string(item, context, g)
    if isinstance(item, Mapping):
        return _sub_dict(item, context, g)
    if isinstance(item, Iterable):
        return _sub_list(item, context, g)
    return item


def _dump_i(obj: Any) -> Any:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, Mapping):
        return {k: _dump_i(v) for k, v in obj.items()}
    if isinstance(obj, Iterable):
        return [_dump_i(i) for i in obj]
    return obj


def _globals(obj: Union[Dict[str, Any], Type[Any]]) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        g = {
            key: getattr(obj, key)
            for key in dir(obj)
            if not key.startswith("_") or key == "__builtins__"
        }
    else:
        g = obj
    return g


def sub(
    obj: Any,
    context: Dict[str, Any] = None,
    values: Dict[str, Any] = None,
    g: Union[Dict[str, Any], Type[Any]] = globals.ExpressionGlobals,
) -> Any:
    context = context or {}
    values = values or {}
    for pointer, value in values.items():
        jsonpointer.set_pointer(context, "/" + pointer, value)
    return _sub_i(obj, context, _globals(g))
