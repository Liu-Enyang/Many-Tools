from __future__ import annotations

import json
from pathlib import Path

from parser.aspx_parser import parse_aspx
from parser.codebehind_parser import parse_codebehind
from parser.spec_parser import parse_spec
from generator.analysis_generator import generate_analysis
from generator.viewpoints_generator import generate_viewpoints
from generator.testcase_generator import generate_testcases
from generator.excel_generator import generate_excel
from generator.checklist_mapper import load_checklist_items, save_checklist_json, attach_checklist_nos_to_confirmations



BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_INPUT_DIR = BASE_DIR / "sample_input"
OUTPUT_DIR = BASE_DIR / "output"


def load_javascript_sources(input_dir: Path) -> list[dict]:
    js_sources: list[dict] = []
    for path in sorted(input_dir.rglob("*.js")):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="shift_jis", errors="ignore")

        js_sources.append(
            {
                "file_name": path.name,
                "relative_path": str(path.relative_to(input_dir)),
                "content": content,
            }
        )
    return js_sources


def load_or_create_checklist() -> list[dict]:
    checklist_json_path = OUTPUT_DIR / "checklist.json"
    checklist_excel_path = SAMPLE_INPUT_DIR / "BR_チェックリスト.xlsx"

    if checklist_json_path.exists():
        with open(checklist_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    if not checklist_excel_path.exists():
        return []

    items = load_checklist_items(checklist_excel_path)
    save_checklist_json(items, checklist_json_path)
    return items


def main() -> None:
    # ▼ 自動検出：ASPX / CS / Excel
    aspx_files = list(SAMPLE_INPUT_DIR.glob("*.aspx"))
    codebehind_files = list(SAMPLE_INPUT_DIR.glob("*.aspx.cs"))
    spec_files = list(SAMPLE_INPUT_DIR.glob("*.xlsx"))

    if not aspx_files:
        raise FileNotFoundError("ASPXファイルが見つかりません。")
    if not codebehind_files:
        raise FileNotFoundError("CodeBehindファイルが見つかりません。")
    if not spec_files:
        raise FileNotFoundError("Excel設計書が見つかりません。")

    aspx_path = aspx_files[0]
    codebehind_path = codebehind_files[0]
    spec_path = spec_files[0]

    aspx_data = parse_aspx(aspx_path)
    codebehind_data = parse_codebehind(codebehind_path)
    spec_data = parse_spec(spec_path)
    javascript_sources = load_javascript_sources(SAMPLE_INPUT_DIR)
    checklist_items = load_or_create_checklist()

    analysis = generate_analysis(
        aspx_data=aspx_data,
        codebehind_data=codebehind_data,
        spec_data=spec_data,
        javascript_sources=javascript_sources,
    )

    viewpoints = generate_viewpoints(analysis)
    testcases = generate_testcases(analysis, viewpoints)
    if checklist_items:
        testcases = attach_checklist_nos_to_confirmations(testcases)

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

    # ▼ Excel（テスト仕様書）生成
    screen_name = analysis.get("screen_name") or "画面"
    safe_name = str(screen_name).replace("/", "_").replace(" ", "_")
    excel_file = OUTPUT_DIR / f"{safe_name}_単体テスト仕様書.xlsx"

    generate_excel(
        json_path=testcases_file,
        output_path=excel_file,
    )

    # print(f"javascript files loaded: {len(javascript_sources)}")
    # print(f"checklist items loaded: {len(checklist_items)}")
    # print(f"analysis.json generated: {analysis_file}")
    # print(f"viewpoints.json generated: {viewpoints_file}")
    # print(f"testcases.json generated: {testcases_file}")
    # print(f"Excel test spec generated: {excel_file}")


if __name__ == "__main__":
    main()