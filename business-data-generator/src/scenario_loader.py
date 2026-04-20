from pathlib import Path
from typing import Any
import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_scenario(base_dir: Path, scenario_id: str) -> dict[str, Any]:
    path = base_dir / "config" / "scenarios" / f"{scenario_id}.yaml"
    return load_yaml(path)


def _find_table_yaml_by_table_name(directory: Path, table_name: str) -> dict[str, Any] | None:
    if not directory.exists():
        return None

    for file in directory.glob("*.yaml"):
        data = load_yaml(file)
        if data.get("table_name") == table_name:
            return data
    return None


def load_table_definition(base_dir: Path, table_name: str) -> dict[str, Any]:
    base_dir_tables = base_dir / "config" / "tables"

    base_yaml = _find_table_yaml_by_table_name(base_dir_tables / "base", table_name)
    if not base_yaml:
        raise FileNotFoundError(f"Base table config not found for: {table_name}")

    # 正式规则优先，其次 rules_draft
    rule_yaml = _find_table_yaml_by_table_name(base_dir_tables / "rules", table_name)
    if not rule_yaml:
        rule_yaml = _find_table_yaml_by_table_name(base_dir_tables / "rules_draft", table_name)

    merged = {
        "table_name": base_yaml.get("table_name"),
        "primary_key": base_yaml.get("primary_key", []),
        "columns": base_yaml.get("columns", []),
        "required_fields": base_yaml.get("required_fields", []),
        "field_sources": {},
        "generated_fields": {},
        "default_values": {},
        "value_candidates": {},
        "analysis": {},
        "warnings": [],
    }

    if rule_yaml:
        merged["field_sources"] = rule_yaml.get("field_sources", {})
        merged["generated_fields"] = rule_yaml.get("generated_fields", {})
        merged["default_values"] = rule_yaml.get("default_values", {})
        merged["value_candidates"] = rule_yaml.get("value_candidates", {})
        merged["analysis"] = rule_yaml.get("analysis", {})
        merged["warnings"] = rule_yaml.get("warnings", [])

    return merged