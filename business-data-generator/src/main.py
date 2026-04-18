from pathlib import Path
import json

from .scenario_loader import load_scenario, load_table
from .value_resolver import build_row
from .sql_builder import build_insert_sql
from .rollback_builder import build_delete_sql
from .schema_to_yaml import process_ddl_folder


def run(base_dir: Path, scenario_id: str, input_file: Path):
    with input_file.open("r", encoding="utf-8") as f:
        input_data = json.load(f)

    scenario = load_scenario(base_dir, scenario_id)

    setup_sql_parts = []
    rollback_sql_parts = []

    for table_item in scenario.get("tables", []):
        table_name = table_item["table"]

        if table_item.get("mode") == "reference_only":
            continue

        include_if = table_item.get("include_if")
        if include_if:
            # only support input.xxx for MVP
            include_key = include_if.split(".", 1)[1]
            if not input_data.get(include_key):
                continue

        table_def = load_table(base_dir, table_name)

        if table_def.get("mode") == "reference_only":
            continue

        if "rows_from" in table_item:
            rows_count = input_data[table_item["rows_from"].split(".", 1)[1]]
        else:
            rows_count = table_item.get("rows", 1)

        rows = [build_row(table_def, input_data, i) for i in range(rows_count)]

        setup_sql_parts.append(build_insert_sql(table_name, rows))
        rollback_sql_parts.append(
            build_delete_sql(table_name, rows, table_def.get("primary_key", []))
        )

    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)

    setup_path = output_dir / f"setup_{scenario_id}.sql"
    rollback_path = output_dir / f"rollback_{scenario_id}.sql"

    setup_path.write_text("\n\n".join(setup_sql_parts), encoding="utf-8")
    rollback_path.write_text("\n\n".join(reversed(rollback_sql_parts)), encoding="utf-8")

    print(f"Generated: {setup_path}")
    print(f"Generated: {rollback_path}")

def run_generate_base_yaml(base_dir: Path, ddl_dir: Path):
    output_dir = base_dir / "config" / "tables" / "base"
    process_ddl_folder(ddl_dir, output_dir)