from pathlib import Path
import argparse

from src.main import run, run_generate_base_yaml
from src.data_to_rule_yaml import process_data_folder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario")
    parser.add_argument("--input")
    parser.add_argument("--ddl-dir")
    parser.add_argument("--data-dir")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent

    # DDL -> base YAML 模式
    if args.ddl_dir:
        ddl_dir = Path(args.ddl_dir).resolve()
        run_generate_base_yaml(base_dir, ddl_dir)
        return

    # CSV -> rule YAML 模式
    if args.data_dir:
        data_dir = Path(args.data_dir).resolve()
        base_yaml_dir = base_dir / "config" / "tables" / "base"
        output_dir = base_dir / "config" / "tables" / "rules_draft"
        process_data_folder(data_dir, base_yaml_dir, output_dir)
        return

    # 场景生成 SQL 模式
    if not args.scenario or not args.input:
        raise ValueError("--scenario and --input are required when not using --ddl-dir or --data-dir")

    input_file = Path(args.input).resolve()
    run(base_dir, args.scenario, input_file)


if __name__ == "__main__":
    main()