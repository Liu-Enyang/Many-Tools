from __future__ import annotations

import json
from pathlib import Path

from parser.aspx_parser import parse_aspx
from parser.codebehind_parser import parse_codebehind
from parser.spec_parser import parse_spec
from generator.analysis_generator import generate_analysis
from generator.viewpoints_generator import generate_viewpoints
from generator.testcase_generator import generate_testcases


BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_INPUT_DIR = BASE_DIR / "sample_input"
OUTPUT_DIR = BASE_DIR / "output"


def main() -> None:
    aspx_path = SAMPLE_INPUT_DIR / "Summary.aspx"
    codebehind_path = SAMPLE_INPUT_DIR / "Summary.aspx.cs"
    spec_path = SAMPLE_INPUT_DIR / "spec.xlsx"

    aspx_data = parse_aspx(aspx_path)
    codebehind_data = parse_codebehind(codebehind_path)
    spec_data = parse_spec(spec_path)

    analysis = generate_analysis(
        aspx_data=aspx_data,
        codebehind_data=codebehind_data,
        spec_data=spec_data,
    )

    viewpoints = generate_viewpoints(analysis)
    testcases = generate_testcases(analysis, viewpoints)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    analysis_file = OUTPUT_DIR / "analysis.json"
    analysis_file.write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    viewpoints_file = OUTPUT_DIR / "viewpoints.json"
    viewpoints_file.write_text(
        json.dumps(viewpoints, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    testcases_file = OUTPUT_DIR / "testcases.json"
    testcases_file.write_text(
        json.dumps(testcases, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"analysis.json generated: {analysis_file}")
    print(f"viewpoints.json generated: {viewpoints_file}")
    print(f"testcases.json generated: {testcases_file}")


if __name__ == "__main__":
    main()