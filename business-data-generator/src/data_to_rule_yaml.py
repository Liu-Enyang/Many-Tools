

from __future__ import annotations

from collections import Counter
from pathlib import Path
import csv
import re
from typing import Any

import yaml


MAX_ENUM_VALUES = 20
MAX_SAMPLED_VALUES = 10
SAMPLE_VALUES_COUNT = 5
TOP_VALUES_COUNT = 10


INPUT_SOURCE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"BranchNo$", re.IGNORECASE), "input.BranchNo"),
    (re.compile(r"CustomerNo$", re.IGNORECASE), "input.CustomerNo"),
    (re.compile(r"KijyunNengetu$", re.IGNORECASE), "input.KijyunNengetu"),
    (re.compile(r"KijunNengetu$", re.IGNORECASE), "input.KijyunNengetu"),
    (re.compile(r"SyoriId$", re.IGNORECASE), "input.SyoriId"),
]


GENERATED_FIELD_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"ShinseiNo$", re.IGNORECASE), "sequence"),
    (re.compile(r"KasitukeNo$", re.IGNORECASE), "row_number"),
]


NOW_FIELD_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"Date$", re.IGNORECASE),
    re.compile(r"Update$", re.IGNORECASE),
    re.compile(r"LastUpdate$", re.IGNORECASE),
    re.compile(r"TourokuDate$", re.IGNORECASE),
]


USER_FIELD_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"UserNo$", re.IGNORECASE),
    re.compile(r"UserId$", re.IGNORECASE),
]


EXCLUDED_CANDIDATE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"No$", re.IGNORECASE),
    re.compile(r"Id$", re.IGNORECASE),
    re.compile(r"Date$", re.IGNORECASE),
    re.compile(r"Update$", re.IGNORECASE),
    re.compile(r"Kingaku$", re.IGNORECASE),
    re.compile(r"Zandaka$", re.IGNORECASE),
    re.compile(r"Riritu$", re.IGNORECASE),
]


NUMERIC_TYPES = {"int", "bigint", "smallint", "tinyint", "decimal", "money", "numeric", "float", "real"}
DATETIME_TYPES = {"date", "datetime", "datetime2", "smalldatetime", "timestamp"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def normalize_cell(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return text


def looks_like_date_yyyymmdd(value: str) -> bool:
    return bool(re.fullmatch(r"\d{8}", value))


def looks_like_datetime_text(value: str) -> bool:
    return bool(
        re.fullmatch(r"\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2})?", value)
        or re.fullmatch(r"\d{4}/\d{2}/\d{2}(?: \d{2}:\d{2}:\d{2})?", value)
    )


def is_excluded_candidate_field(column_name: str) -> bool:
    return any(pattern.search(column_name) for pattern in EXCLUDED_CANDIDATE_PATTERNS)


def infer_input_source(column_name: str) -> str | None:
    for pattern, source in INPUT_SOURCE_PATTERNS:
        if pattern.search(column_name):
            return source
    return None


def infer_generated_rule(column_name: str) -> str | None:
    for pattern, rule in GENERATED_FIELD_PATTERNS:
        if pattern.search(column_name):
            return rule
    return None


def infer_default_value(column_name: str, column_type: str) -> tuple[Any, str] | None:
    if any(pattern.search(column_name) for pattern in USER_FIELD_PATTERNS):
        return "TESTUSER", "inferred_from_name"

    if column_type.lower() in DATETIME_TYPES:
        return "@@now", "inferred_from_type"

    if any(pattern.search(column_name) for pattern in NOW_FIELD_PATTERNS):
        return "@@now", "inferred_from_name"

    if column_type.lower() in {"tinyint", "smallint", "int"}:
        return 0, "inferred_from_type"

    return None


def build_column_map(base_yaml: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {col["name"]: col for col in base_yaml.get("columns", []) if isinstance(col, dict) and "name" in col}


def profile_csv(csv_path: Path) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    total_rows = 0
    print(f"   🔍 Profiling CSV: {csv_path.name}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return {}

        for field in reader.fieldnames:
            stats[field] = {
                "non_null_count": 0,
                "null_count": 0,
                "counter": Counter(),
                "sample_values": [],
                "date_like_count": 0,
                "datetime_like_count": 0,
            }

        for row in reader:
            total_rows += 1
            if total_rows % 1000 == 0:
                print(f"   ⏳ Profiling rows: {total_rows}", end="\r")
            for field in reader.fieldnames:
                value = normalize_cell(row.get(field))
                field_stat = stats[field]
                if value is None:
                    field_stat["null_count"] += 1
                    continue

                field_stat["non_null_count"] += 1
                field_stat["counter"][value] += 1

                if len(field_stat["sample_values"]) < SAMPLE_VALUES_COUNT and value not in field_stat["sample_values"]:
                    field_stat["sample_values"].append(value)

                if looks_like_date_yyyymmdd(value):
                    field_stat["date_like_count"] += 1
                if looks_like_datetime_text(value):
                    field_stat["datetime_like_count"] += 1

    print(f"   ✅ Profiling completed. Total rows: {total_rows}")
    result: dict[str, dict[str, Any]] = {}
    for field, field_stat in stats.items():
        counter: Counter[str] = field_stat["counter"]
        distinct_count = len(counter)
        non_null_count = field_stat["non_null_count"]
        null_count = field_stat["null_count"]
        row_count = total_rows
        null_ratio = round((null_count / row_count), 4) if row_count else 0.0

        top_values = [value for value, _ in counter.most_common(TOP_VALUES_COUNT)]
        all_values = list(counter.keys())

        result[field] = {
            "row_count": row_count,
            "non_null_count": non_null_count,
            "null_count": null_count,
            "null_ratio": null_ratio,
            "distinct_count": distinct_count,
            "sample_values": field_stat["sample_values"],
            "top_values": top_values,
            "all_values": all_values,
            "date_like_ratio": round((field_stat["date_like_count"] / non_null_count), 4) if non_null_count else 0.0,
            "datetime_like_ratio": round((field_stat["datetime_like_count"] / non_null_count), 4) if non_null_count else 0.0,
        }

    return result


def build_value_candidates(column_name: str, profile: dict[str, Any]) -> dict[str, Any] | None:
    if is_excluded_candidate_field(column_name):
        return None

    distinct_count = profile.get("distinct_count", 0)
    all_values = profile.get("all_values", [])
    top_values = profile.get("top_values", [])

    if distinct_count == 0:
        return None

    if distinct_count <= MAX_ENUM_VALUES:
        return {
            "type": "enum",
            "values": all_values,
            "source": "csv_all_values",
        }

    if distinct_count <= 200:
        return {
            "type": "sampled",
            "values": top_values[:MAX_SAMPLED_VALUES],
            "source": "csv_top_values",
            "note": f"distinct_count={distinct_count}",
        }

    return None


def infer_csv_default(column_name: str, profile: dict[str, Any], column_type: str) -> tuple[Any, str] | None:
    top_values = profile.get("top_values", [])
    all_values = profile.get("all_values", [])
    distinct_count = profile.get("distinct_count", 0)
    non_null_count = profile.get("non_null_count", 0)

    if non_null_count == 0:
        return None

    if any(pattern.search(column_name) for pattern in USER_FIELD_PATTERNS):
        return "TESTUSER", "inferred_from_name"

    if column_type.lower() in DATETIME_TYPES and profile.get("datetime_like_ratio", 0.0) >= 0.7:
        return "@@now", "inferred_from_csv_and_type"

    if column_type.lower() == "char" and profile.get("date_like_ratio", 0.0) >= 0.7 and top_values:
        sample = top_values[0]
        if looks_like_date_yyyymmdd(sample):
            return "@@today_yyyymmdd", "inferred_from_csv_and_name"

    if distinct_count == 1 and len(all_values) == 1:
        return all_values[0], "csv_single_value"

    counter_preview = top_values[:1]
    if counter_preview and distinct_count <= MAX_ENUM_VALUES:
        return counter_preview[0], "csv_top_value"

    return None


def build_rule_yaml_from_base(
    base_yaml: dict[str, Any],
    csv_profile: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    table_name = base_yaml.get("table_name")
    columns = base_yaml.get("columns", [])
    required_fields = base_yaml.get("required_fields", [])

    field_sources: dict[str, Any] = {}
    generated_fields: dict[str, Any] = {}
    default_values: dict[str, Any] = {}
    value_candidates: dict[str, Any] = {}
    analysis: dict[str, Any] = {}
    warnings: list[str] = []

    rule_sources = ["ddl_inference"]
    if csv_profile:
        rule_sources.append("csv_analysis")
    else:
        warnings.append("No CSV found. Falling back to DDL-based rule inference.")

    for column in columns:
        column_name = column.get("name")
        column_type = str(column.get("type", "")).lower()
        nullable = bool(column.get("nullable", True))
        if not column_name:
            continue

        input_source = infer_input_source(column_name)
        if input_source:
            field_sources[column_name] = {
                "value": input_source,
                "source": "inferred_from_name",
            }

        generated_rule = infer_generated_rule(column_name)
        if generated_rule:
            generated_fields[column_name] = {
                "value": generated_rule,
                "source": "inferred_from_name",
            }

        profile = (csv_profile or {}).get(column_name)
        if profile:
            analysis[column_name] = {
                "distinct_count": profile.get("distinct_count", 0),
                "null_ratio": profile.get("null_ratio", 0.0),
                "sample_values": profile.get("sample_values", []),
                "top_values": profile.get("top_values", []),
            }

            candidate_info = build_value_candidates(column_name, profile)
            if candidate_info:
                value_candidates[column_name] = candidate_info

            csv_default = infer_csv_default(column_name, profile, column_type)
            if csv_default and column_name not in default_values and column_name not in field_sources and column_name not in generated_fields:
                default_values[column_name] = {
                    "value": csv_default[0],
                    "source": csv_default[1],
                }

        inferred_default = infer_default_value(column_name, column_type)
        if (
            inferred_default
            and column_name not in default_values
            and column_name not in field_sources
            and column_name not in generated_fields
        ):
            default_values[column_name] = {
                "value": inferred_default[0],
                "source": inferred_default[1],
            }

        if not nullable and column_name in required_fields:
            has_rule = (
                column_name in field_sources
                or column_name in generated_fields
                or column_name in default_values
            )
            if not has_rule:
                warnings.append(f"Required field has no inferred rule: {column_name}")

    rule_yaml = {
        "table_name": table_name,
        "metadata": {
            "rule_source": rule_sources,
            "has_csv": bool(csv_profile),
        },
        "field_sources": field_sources,
        "generated_fields": generated_fields,
        "default_values": default_values,
        "value_candidates": value_candidates,
        "analysis": analysis,
        "warnings": warnings,
    }

    return rule_yaml


def generate_rule_yaml_for_table(
    base_yaml_path: Path,
    csv_path: Path | None,
    output_path: Path,
) -> None:
    base_yaml = load_yaml(base_yaml_path)
    csv_profile = profile_csv(csv_path) if csv_path and csv_path.exists() else None
    rule_yaml = build_rule_yaml_from_base(base_yaml, csv_profile)
    write_yaml(output_path, rule_yaml)


def process_data_folder(
    data_dir: Path,
    base_yaml_dir: Path,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    base_files = sorted(base_yaml_dir.glob("*.yaml"))
    total = len(base_files)

    print(f"📂 Scanning Base YAML folder: {base_yaml_dir}")
    print(f"📄 Found {total} base YAML files")

    if total == 0:
        print("⚠️ No base YAML files found. Nothing to process.")
        return

    for idx, base_yaml_path in enumerate(base_files, start=1):
        base_yaml = load_yaml(base_yaml_path)
        table_name = base_yaml.get("table_name")
        if not table_name:
            print(f"⚠️ Skip invalid base yaml: {base_yaml_path.name}")
            continue

        csv_path = data_dir / f"{table_name}.csv"
        if not csv_path.exists():
            csv_path = data_dir / f"{table_name.lower()}.csv"

        output_path = output_dir / base_yaml_path.name

        print(f"➡️ Processing ({idx}/{total}): {table_name}")
        if csv_path.exists():
            print(f"   📊 CSV found: {csv_path.name}")
        else:
            print(f"   ⚠️ No CSV found. Use DDL inference only.")

        generate_rule_yaml_for_table(base_yaml_path, csv_path if csv_path.exists() else None, output_path)
        print(f"   ✅ Generated: {output_path.name}")

    print("🎉 All rule YAML draft files processed.")