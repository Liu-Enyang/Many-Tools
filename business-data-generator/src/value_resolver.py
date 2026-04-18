from datetime import datetime


def resolve_input_path(data: dict, path: str):
    # path example: input.BranchNo
    parts = path.split(".")
    if parts[0] != "input":
        raise ValueError(f"Unsupported source path: {path}")
    value = data
    for p in parts[1:]:
        value = value[p]
    return value


def resolve_value(field_name: str, table_def: dict, input_data: dict, row_index: int):
    field_sources = table_def.get("field_sources", {})
    default_values = table_def.get("default_values", {})
    generated_fields = table_def.get("generated_fields", {})

    if field_name in field_sources:
        return resolve_input_path(input_data, field_sources[field_name])

    if field_name in generated_fields:
        rule = generated_fields[field_name]
        if rule == "sequence":
            return 1000000000 + row_index
        if rule == "row_number":
            return row_index + 1
        raise ValueError(f"Unsupported generated rule: {rule}")

    if field_name in default_values:
        value = default_values[field_name]
        if value == "@@now":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return value

    return None


def build_row(table_def: dict, input_data: dict, row_index: int) -> dict:
    fields = table_def.get("required_fields", [])
    row = {}
    for field in fields:
        row[field] = resolve_value(field, table_def, input_data, row_index)
    return row