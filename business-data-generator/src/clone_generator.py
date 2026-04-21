from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml

from .dictionary_loader import (
    find_dictionary_csv,
    load_field_dictionary_mapping,
    load_pcc_hanyou_dictionary,
    open_csv_with_fallback,
)
from .sql_builder import build_insert_sql
from .rollback_builder import build_delete_sql


def _load_base_yaml(config_dir: Path, table_name: str) -> dict[str, Any]:
    candidates = [
        config_dir / "tables" / "base" / f"{table_name.lower()}.yaml",
        config_dir / "tables" / "base" / f"{table_name}.yaml",
    ]
    for p in candidates:
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    raise FileNotFoundError(f"Base YAML not found for table: {table_name}")


def _read_csv_rows(data_dir: Path, table_name: str) -> list[dict[str, str]]:
    csv_path = find_dictionary_csv(data_dir, table_name)
    if not csv_path:
        raise FileNotFoundError(f"CSV not found for table: {table_name}")
    print(f"   CSV: {csv_path.name}")
    f, encoding = open_csv_with_fallback(csv_path)
    with f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def _get_column_info(base_yaml: dict, field_name: str) -> dict:
    for col in base_yaml.get("columns", []):
        if col["name"] == field_name:
            return col
    return {}


def _max_plus_one(values: list[str], col_type: str, col_length: str | None) -> str:
    nums = []
    for v in values:
        v = v.strip().strip('"')
        try:
            nums.append(int(float(v)))
        except (ValueError, TypeError):
            pass
    new_val = (max(nums) + 1) if nums else 1

    # char型の数値文字列: 元の桁数でゼロ埋め
    if col_type == "char" and col_length:
        try:
            return str(new_val).zfill(int(col_length))
        except (ValueError, TypeError):
            pass
    return str(new_val)


def _pick_row(rows: list[dict], table_name: str) -> dict[str, str]:
    print(f"\n[TABLE] {table_name}  ({len(rows)} rows)")
    for i, row in enumerate(rows):
        preview = "  |  ".join(f"{k}={v!r}" for k, v in list(row.items())[:5])
        print(f"  [{i}] {preview}")

    while True:
        choice = input(f"\nSelect row [0-{len(rows)-1}] (default 0): ").strip()
        if choice == "":
            return rows[0]
        try:
            idx = int(choice)
            if 0 <= idx < len(rows):
                return rows[idx]
        except ValueError:
            pass
        print("  Invalid. Try again.")


def _interactive_kubun(
    row: dict[str, str],
    field_mapping: dict[str, Any],
    dictionaries: dict[str, dict[str, dict[str, str]]],
) -> dict[str, str]:
    kubun_fields = [f for f in row if f in field_mapping]
    if not kubun_fields:
        print("\n[WARN] No kubun fields for this table in field_dictionary_mapping.yaml")
        return {}

    overrides: dict[str, str] = {}
    print(f"\n[KUBUN] {len(kubun_fields)} kubun field(s) found. Enter to keep current.")

    for field in kubun_fields:
        mapping = field_mapping[field]
        code_key = mapping.get("code_key", "")
        description = mapping.get("description", field)
        current = row.get(field, "").strip()
        options = list(dictionaries.get(code_key, {}).items())

        print(f"\n  >> {field}  [{description}]")
        print(f"     Current: {current!r}")

        if not options:
            print(f"     (No options in PCC_hanyou for code_key={code_key!r})")
            continue

        for i, (code, meta) in enumerate(options):
            stored = meta.get("unique_key", code)
            marker = " <-- current" if stored == current else ""
            print(f"     [{i+1:>2}] {meta.get('label', code):<30} ({stored}){marker}")

        while True:
            choice = input(f"     Select [1-{len(options)}] or Enter to keep: ").strip()
            if choice == "":
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    stored = options[idx][1].get("unique_key", options[idx][0])
                    overrides[field] = stored
                    print(f"     -> {stored}")
                    break
            except ValueError:
                pass
            print("     Invalid. Try again.")

    return overrides


def run_clone(base_dir: Path, table_name: str) -> None:
    data_dir = base_dir / "data"
    config_dir = base_dir / "config"
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n[CLONE] {table_name}")

    rows = _read_csv_rows(data_dir, table_name)
    if not rows:
        print(f"[ERROR] No rows in CSV for {table_name}")
        return

    base_yaml = _load_base_yaml(config_dir, table_name)
    primary_keys: list[str] = base_yaml.get("primary_key", [])

    source_row = _pick_row(rows, table_name)
    new_row = dict(source_row)

    # PK: max+1
    print("\n[PK] Primary key -> max+1:")
    for pk in primary_keys:
        all_vals = [r.get(pk, "") for r in rows]
        col_info = _get_column_info(base_yaml, pk)
        new_val = _max_plus_one(all_vals, col_info.get("type", ""), col_info.get("length"))
        print(f"   {pk}: {source_row.get(pk, '')!r} -> {new_val!r}")
        new_row[pk] = new_val

    # 区分: interactive
    try:
        field_mapping = load_field_dictionary_mapping(config_dir)
        dictionaries = load_pcc_hanyou_dictionary(data_dir, config_dir)
        overrides = _interactive_kubun(new_row, field_mapping, dictionaries)
        new_row.update(overrides)
    except FileNotFoundError as e:
        print(f"\n[WARN] Skipping kubun selection: {e}")

    # empty string -> None (SQL NULL)
    final_row = {k: (None if v == "" else v) for k, v in new_row.items()}

    insert_sql = build_insert_sql(table_name, [final_row])
    delete_sql = build_delete_sql(table_name, [final_row], primary_keys)

    out_insert = output_dir / f"clone_{table_name}.sql"
    out_rollback = output_dir / f"rollback_clone_{table_name}.sql"
    out_insert.write_text(insert_sql, encoding="utf-8")
    out_rollback.write_text(delete_sql, encoding="utf-8")

    print(f"\n[OK] Output:")
    print(f"   INSERT   -> {out_insert}")
    print(f"   ROLLBACK -> {out_rollback}")
    print(f"\n{'-'*60}")
    print(insert_sql)
    print(f"\n{'-'*60}")
    print(delete_sql)
