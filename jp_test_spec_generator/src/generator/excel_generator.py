from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


THIN_SIDE = Side(style="thin", color="000000")
HEADER_FILL = PatternFill("solid", fgColor="D9E2F3")
SECTION_FILL = PatternFill("solid", fgColor="BDD7EE")
SUBHEADER_FILL = PatternFill("solid", fgColor="E2F0D9")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

# PCL colors
PCL_COLOR_MAP = {
    "N": PatternFill("solid", fgColor="C6EFCE"),  # green
    "E": PatternFill("solid", fgColor="FFC7CE"),  # red
    "L": PatternFill("solid", fgColor="FFEB9C"),  # yellow
    "I": PatternFill("solid", fgColor="BDD7EE"),  # blue
}


class ExcelGenerationError(Exception):
    pass



def _load_json(json_path: str | Path) -> Dict[str, Any]:
    path = Path(json_path)
    if not path.exists():
        raise ExcelGenerationError(f"JSON file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ExcelGenerationError("Invalid JSON structure: root must be an object")

    return data



def _validate_testcases(data: Dict[str, Any]) -> None:
    if "definitions" not in data:
        raise ExcelGenerationError("Invalid JSON structure: 'definitions' is required")
    if "test_cases" not in data:
        raise ExcelGenerationError("Invalid JSON structure: 'test_cases' is required")

    definitions = data["definitions"]
    required_definition_keys = ["check_conditions", "actions", "confirmations"]
    for key in required_definition_keys:
        if key not in definitions:
            raise ExcelGenerationError(f"Invalid JSON structure: 'definitions.{key}' is required")



def _build_definition_map(definitions: List[Dict[str, str]]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for item in definitions:
        item_id = str(item.get("id", "")).strip()
        text = str(item.get("text", "")).strip()
        if not item_id or not text:
            continue
        result[item_id] = text
    return result



def _apply_border_range(ws, start_row: int, end_row: int, start_col: int, end_col: int) -> None:
    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            ws.cell(row=row, column=col).border = Border(
                left=THIN_SIDE,
                right=THIN_SIDE,
                top=THIN_SIDE,
                bottom=THIN_SIDE,
            )



def _set_column_widths(ws, case_count: int) -> None:
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 48

    case_start_col = 4
    for offset in range(case_count):
        ws.column_dimensions[get_column_letter(case_start_col + offset)].width = 10



def _write_title(ws, screen_id: str, screen_name: str, case_count: int) -> int:
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(4, 3 + case_count))
    title_cell = ws.cell(row=1, column=1)
    title_cell.value = f"単体テスト仕様書マトリクス - {screen_id} {screen_name}".strip()
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = LEFT
    title_cell.fill = HEADER_FILL

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=2)
    ws.cell(row=2, column=1).value = "画面ID"
    ws.cell(row=2, column=1).font = Font(bold=True)
    ws.cell(row=2, column=1).alignment = CENTER
    ws.cell(row=2, column=1).fill = SUBHEADER_FILL
    ws.cell(row=2, column=3).value = screen_id
    ws.cell(row=2, column=3).alignment = LEFT

    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=2)
    ws.cell(row=3, column=1).value = "画面名"
    ws.cell(row=3, column=1).font = Font(bold=True)
    ws.cell(row=3, column=1).alignment = CENTER
    ws.cell(row=3, column=1).fill = SUBHEADER_FILL
    ws.cell(row=3, column=3).value = screen_name
    ws.cell(row=3, column=3).alignment = LEFT

    return 5



def _write_case_header(ws, start_row: int, test_cases: List[Dict[str, Any]]) -> int:
    ws.cell(row=start_row, column=1).value = "区分"
    ws.cell(row=start_row, column=2).value = "項番"
    ws.cell(row=start_row, column=3).value = "内容"

    for col in range(1, 4):
        cell = ws.cell(row=start_row, column=col)
        cell.font = Font(bold=True)
        cell.alignment = CENTER
        cell.fill = HEADER_FILL

    case_start_col = 4
    for index, test_case in enumerate(test_cases):
        col = case_start_col + index
        header_cell = ws.cell(row=start_row, column=col)
        header_cell.value = test_case.get("case_no") or test_case.get("case_id")
        header_cell.font = Font(bold=True)
        header_cell.alignment = CENTER
        header_cell.fill = HEADER_FILL

    return start_row + 1


# Write PCL row under case header
def _write_pcl_row(ws, start_row: int, test_cases: List[Dict[str, Any]]) -> int:
    """Write PCL row under case header"""
    # left labels
    ws.cell(row=start_row, column=1).value = "PCL"
    ws.cell(row=start_row, column=1).font = Font(bold=True)
    ws.cell(row=start_row, column=1).alignment = CENTER
    ws.cell(row=start_row, column=1).fill = SUBHEADER_FILL

    ws.cell(row=start_row, column=2).value = ""
    ws.cell(row=start_row, column=3).value = ""

    case_start_col = 4

    for index, test_case in enumerate(test_cases):
        col = case_start_col + index
        cell = ws.cell(row=start_row, column=col)

        pcl_list = test_case.get("pcl", [])
        pcl_text = ",".join(pcl_list) if pcl_list else "N"
        cell.value = pcl_text
        cell.alignment = CENTER

        # apply color (if multiple, use first for color)
        if pcl_list:
            color_key = pcl_list[0]
        else:
            color_key = "N"

        fill = PCL_COLOR_MAP.get(color_key)
        if fill:
            cell.fill = fill

    return start_row + 1



def _write_section(
    ws,
    start_row: int,
    section_title: str,
    items: List[Dict[str, str]],
    test_cases: List[Dict[str, Any]],
    relation_key: str,
) -> int:
    if not items:
        return start_row

    case_start_col = 4
    section_start_row = start_row
    section_end_row = start_row + len(items)

    ws.merge_cells(start_row=section_start_row, start_column=1, end_row=section_end_row, end_column=1)
    section_cell = ws.cell(row=section_start_row, column=1)
    section_cell.value = section_title
    section_cell.font = Font(bold=True)
    section_cell.alignment = CENTER
    section_cell.fill = SECTION_FILL

    for item_index, item in enumerate(items, start=1):
        row = start_row + item_index - 1
        item_id = str(item.get("id", "")).strip()
        item_text = str(item.get("text", "")).strip()

        no_cell = ws.cell(row=row, column=2)
        no_cell.value = item_id
        no_cell.alignment = CENTER

        text_cell = ws.cell(row=row, column=3)
        text_cell.value = item_text
        text_cell.alignment = LEFT

        for case_index, test_case in enumerate(test_cases):
            col = case_start_col + case_index
            cell = ws.cell(row=row, column=col)
            related_ids = test_case.get(relation_key, [])
            cell.value = "○" if item_id in related_ids else ""
            cell.alignment = CENTER

    _apply_border_range(ws, section_start_row, section_end_row, 1, 3 + len(test_cases))
    return section_end_row + 1



def _write_case_detail_sheet(wb: Workbook, test_cases: List[Dict[str, Any]]) -> None:
    ws = wb.create_sheet("CaseList")
    headers = [
        "case_no",
        "case_id",
        "category",
        "test_viewpoint_id",
        "test_viewpoint",
        "check_condition_ids",
        "action_ids",
        "confirmation_ids",
        "source_basis",
    ]

    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = CENTER
        cell.fill = HEADER_FILL

    for row_index, test_case in enumerate(test_cases, start=2):
        ws.cell(row=row_index, column=1).value = test_case.get("case_no")
        ws.cell(row=row_index, column=2).value = test_case.get("case_id")
        ws.cell(row=row_index, column=3).value = test_case.get("category")
        ws.cell(row=row_index, column=4).value = test_case.get("test_viewpoint_id")
        ws.cell(row=row_index, column=5).value = test_case.get("test_viewpoint")
        ws.cell(row=row_index, column=6).value = ", ".join(test_case.get("check_condition_ids", []))
        ws.cell(row=row_index, column=7).value = ", ".join(test_case.get("action_ids", []))
        ws.cell(row=row_index, column=8).value = ", ".join(test_case.get("confirmation_ids", []))
        ws.cell(row=row_index, column=9).value = ", ".join(test_case.get("source_basis", []))

    widths = {
        "A": 12,
        "B": 12,
        "C": 14,
        "D": 16,
        "E": 36,
        "F": 20,
        "G": 20,
        "H": 20,
        "I": 30,
    }
    for col_letter, width in widths.items():
        ws.column_dimensions[col_letter].width = width

    _apply_border_range(ws, 1, max(2, len(test_cases) + 1), 1, len(headers))



def generate_excel(
    json_path: str | Path,
    output_path: str | Path,
    sheet_name: str = "TestSpec",
) -> Path:
    data = _load_json(json_path)
    _validate_testcases(data)

    screen_id = str(data.get("screen_id", "")).strip()
    screen_name = str(data.get("screen_name", "")).strip()
    definitions = data["definitions"]
    test_cases = data.get("test_cases", [])

    check_conditions = definitions.get("check_conditions", [])
    actions = definitions.get("actions", [])
    confirmations = definitions.get("confirmations", [])

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.freeze_panes = "D8"
    ws.sheet_view.showGridLines = False

    row = _write_title(ws, screen_id, screen_name, len(test_cases))
    row = _write_case_header(ws, row, test_cases)
    row = _write_pcl_row(ws, row, test_cases)
    row = _write_section(ws, row, "チェック条件", check_conditions, test_cases, "check_condition_ids")
    row = _write_section(ws, row, "アクション", actions, test_cases, "action_ids")
    row = _write_section(ws, row, "確認内容", confirmations, test_cases, "confirmation_ids")

    _set_column_widths(ws, len(test_cases))
    _apply_border_range(ws, 1, row - 1, 1, 3 + len(test_cases))

    definition_map_sheet = wb.create_sheet("Definitions")
    definition_headers = ["type", "id", "text"]
    for col, header in enumerate(definition_headers, start=1):
        cell = definition_map_sheet.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = CENTER
        cell.fill = HEADER_FILL

    definition_row = 2
    for section_type, section_items in [
        ("check_condition", check_conditions),
        ("action", actions),
        ("confirmation", confirmations),
    ]:
        for item in section_items:
            definition_map_sheet.cell(row=definition_row, column=1).value = section_type
            definition_map_sheet.cell(row=definition_row, column=2).value = item.get("id")
            definition_map_sheet.cell(row=definition_row, column=3).value = item.get("text")
            definition_row += 1

    definition_map_sheet.column_dimensions["A"].width = 18
    definition_map_sheet.column_dimensions["B"].width = 12
    definition_map_sheet.column_dimensions["C"].width = 60
    _apply_border_range(definition_map_sheet, 1, max(2, definition_row - 1), 1, 3)

    _write_case_detail_sheet(wb, test_cases)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    return output



def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate Excel test specification from testcases.json")
    parser.add_argument("json_path", help="Path to testcases.json")
    parser.add_argument("output_path", help="Path to output .xlsx file")
    parser.add_argument("--sheet-name", default="TestSpec", help="Main sheet name")
    args = parser.parse_args()

    output = generate_excel(
        json_path=args.json_path,
        output_path=args.output_path,
        sheet_name=args.sheet_name,
    )
    print(f"Excel generated: {output}")


if __name__ == "__main__":
    main()
