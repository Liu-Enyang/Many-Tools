from pathlib import Path
import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_scenario(base_dir: Path, scenario_id: str) -> dict:
    path = base_dir / "config" / "scenarios" / f"{scenario_id}.yaml"
    return load_yaml(path)


def load_table(base_dir: Path, table_name: str) -> dict:
    tables_dir = base_dir / "config" / "tables"

    # 遍历所有 table yaml，找匹配 table_name 的
    for file in tables_dir.glob("*.yaml"):
        data = load_yaml(file)
        if data.get("table_name") == table_name:
            return data

    raise FileNotFoundError(f"Table config not found for: {table_name}")