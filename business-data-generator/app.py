from pathlib import Path
import argparse

from src.main import run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    input_file = Path(args.input).resolve()

    run(base_dir, args.scenario, input_file)


if __name__ == "__main__":
    main()