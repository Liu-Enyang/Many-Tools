from __future__ import annotations

from datetime import datetime
from typing import Any


def resolve_input_path(data: dict[str, Any], path: str) -> Any:
    parts = path.split(".")
    if parts[0] != "input":
        raise ValueError(f"Unsupported source path: {path}")

    value: Any = data
    for p in parts[1:]:
        if not isinstance(value, dict) or p not in value:
            raise KeyError(f"Input value not found for path: {path}")
        value = value[p]
    return value


def unwrap_rule_value(rule: Any) -> Any:
    if isinstance(rule, dict) and "value" in rule:
        return rule["value"]
    return rule


def resolve_special_token(value: Any) -> Any:
    if value == "@@now":
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if value == "@@today_yyyymmdd":
        return datetime.now().strftime("%Y%m%d")
    return value


def resolve_generated_value(rule: str, row_index: int) -> Any:
    if rule == "sequence":
        return 1000000000 + row_index
    if rule == "row_number":
        return row_index + 1
    raise ValueError(f"Unsupported generated rule: {rule}")


def resolve_value(field_name: str, table_def: dict[str, Any], input_data: dict[str, Any], row_index: int) -> Any:
    field_sources = table_def.get("field_sources", {})
    default_values = table_def.get("default_values", {})
    generated_fields = table_def.get("generated_fields", {})

    if field_name in field_sources:
        raw = unwrap_rule_value(field_sources[field_name])
        if isinstance(raw, str) and raw.startswith("input."):
            return resolve_input_path(input_data, raw)
        return resolve_special_token(raw)

    if field_name in generated_fields:
        raw = unwrap_rule_value(generated_fields[field_name])
        return resolve_generated_value(str(raw), row_index)

    if field_name in default_values:
        raw = unwrap_rule_value(default_values[field_name])
        return resolve_special_token(raw)

    return None


def build_row(table_def: dict[str, Any], input_data: dict[str, Any], row_index: int) -> dict[str, Any]:
    fields = table_def.get("required_fields", [])
    row: dict[str, Any] = {}

    for field in fields:
        row[field] = resolve_value(field, table_def, input_data, row_index)

    return row