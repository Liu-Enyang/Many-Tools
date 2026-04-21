

from __future__ import annotations

from pathlib import Path
import csv
from typing import Any

import yaml


CSV_ENCODINGS = ["utf-8-sig", "cp932", "shift_jis", "utf-8"]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def open_csv_with_fallback(csv_path: Path):
    last_error: Exception | None = None
    for encoding in CSV_ENCODINGS:
        try:
            f = csv_path.open("r", encoding=encoding, newline="")
            f.read(1024)
            f.seek(0)
            return f, encoding
        except UnicodeDecodeError as e:
            last_error = e
        except Exception as e:
            last_error = e
    raise RuntimeError(f"Unable to read CSV with supported encodings: {csv_path}") from last_error


def find_dictionary_csv(data_dir: Path, table_name: str) -> Path | None:
    candidates = [
        data_dir / f"{table_name}.csv",
        data_dir / f"{table_name.lower()}.csv",
        data_dir / f"dbo.{table_name}.csv",
        data_dir / f"dbo.{table_name.lower()}.csv",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    table_name_lower = table_name.lower()
    for candidate in sorted(data_dir.glob("*.csv")):
        stem_lower = candidate.stem.lower()
        if stem_lower == table_name_lower:
            return candidate
        if stem_lower.endswith(f".{table_name_lower}"):
            return candidate

    return None


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def load_dictionary_definition(config_dir: Path, dictionary_name: str = "pcc_hanyou_definition") -> dict[str, Any]:
    definition_path = config_dir / "dictionaries" / f"{dictionary_name}.yaml"
    return load_yaml(definition_path)


def load_field_dictionary_mapping(config_dir: Path) -> dict[str, Any]:
    mapping_path = config_dir / "dictionaries" / "field_dictionary_mapping.yaml"
    data = load_yaml(mapping_path)
    return data.get("field_dictionary_mapping", {})


def load_pcc_hanyou_dictionary(data_dir: Path, config_dir: Path) -> dict[str, dict[str, dict[str, str]]]:
    definition = load_dictionary_definition(config_dir, "pcc_hanyou_definition")
    table_name = definition.get("table_name", "PCC_hanyou")
    dictionary_definition = definition.get("dictionary_definition", {})

    key_field = dictionary_definition.get("key_field")
    value_field = dictionary_definition.get("value_field")
    label_field = dictionary_definition.get("label_field")
    description_field = dictionary_definition.get("description_field")
    unique_key_field = dictionary_definition.get("unique_key_field")

    if not key_field or not value_field or not label_field:
        raise ValueError("Dictionary definition is missing required fields.")

    csv_path = find_dictionary_csv(data_dir, table_name)
    if not csv_path:
        raise FileNotFoundError(f"Dictionary CSV not found for table: {table_name}")

    print(f"[DICT] Loading dictionary: {table_name}")
    print(f"   CSV found: {csv_path.name}")

    file_obj, encoding = open_csv_with_fallback(csv_path)
    print(f"   CSV encoding: {encoding}")

    dictionaries: dict[str, dict[str, dict[str, str]]] = {}

    with file_obj as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return {}

        for row in reader:
            code_key = _normalize_text(row.get(key_field))
            code_value = _normalize_text(row.get(value_field))
            label = _normalize_text(row.get(label_field))
            description = _normalize_text(row.get(description_field)) if description_field else ""

            if not code_key or not code_value:
                continue

            if code_key not in dictionaries:
                dictionaries[code_key] = {}

            unique_key = _normalize_text(row.get(unique_key_field)) if unique_key_field else ""
            dictionaries[code_key][code_value] = {
                "label": label or code_value,
                "description": description,
                "unique_key": unique_key or code_value,
            }

    print(f"   Dictionary loaded. Code groups: {len(dictionaries)}")
    return dictionaries


def resolve_dictionary_for_field(
    field_name: str,
    mapping: dict[str, Any],
    dictionaries: dict[str, dict[str, dict[str, str]]],
) -> dict[str, Any] | None:
    field_mapping = mapping.get(field_name)
    if not field_mapping:
        return None

    code_key = field_mapping.get("code_key")
    if not code_key:
        return None

    return {
        "field_name": field_name,
        "table": field_mapping.get("table", "PCC_hanyou"),
        "code_key": code_key,
        "description": field_mapping.get("description", ""),
        "values": dictionaries.get(code_key, {}),
    }


def format_dictionary_options_for_display(dictionary_info: dict[str, Any]) -> list[str]:
    values = dictionary_info.get("values", {})
    result: list[str] = []

    for code, meta in values.items():
        label = meta.get("label", code)
        result.append(f"{label} ({code})")

    return result