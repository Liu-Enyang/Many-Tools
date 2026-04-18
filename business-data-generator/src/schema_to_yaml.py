from pathlib import Path
import yaml
from .schema_parser import parse_ddl


def convert_ddl_to_yaml(sql_file: Path, output_dir: Path):
    sql_text = sql_file.read_text(encoding="utf-8")
    parsed = parse_ddl(sql_text)

    if not parsed["table_name"]:
        print(f"⚠️ Skip: {sql_file.name}")
        return

    table_name = parsed["table_name"]

    yaml_data = {
        "table_name": table_name,
        "primary_key": parsed["primary_key"],
        "columns": parsed["columns"],
        "required_fields": [
            col["name"] for col in parsed["columns"] if not col["nullable"]
        ],
        "primary_key_count": len(parsed["primary_key"]),
    }

    output_file = output_dir / f"{table_name.lower()}.yaml"
    output_file.write_text(
        yaml.dump(yaml_data, allow_unicode=True, sort_keys=False),
        encoding="utf-8"
    )

    print(f"✅ Generated: {output_file.name}")


def process_ddl_folder(input_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    files = list(input_dir.glob("*.sql"))
    total = len(files)

    print(f"📂 Scanning DDL folder: {input_dir}")
    print(f"📄 Found {total} SQL files")

    if total == 0:
        print("⚠️ No SQL files found. Nothing to process.")
        return

    for idx, file in enumerate(files, start=1):
        print(f"➡️ Processing ({idx}/{total}): {file.name}")
        convert_ddl_to_yaml(file, output_dir)

    print("🎉 All DDL files processed.")