from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _guess_screen_id(aspx_data: Dict[str, Any]) -> str:
    file_name = Path(aspx_data.get("file", "")).stem
    return file_name or "UnknownScreen"


def _guess_screen_name(aspx_data: Dict[str, Any]) -> str:
    for control in aspx_data.get("controls", []):
        if control.get("type") == "Label" and control.get("text"):
            return control["text"]

    # 从页面中常见标题控制
    return "画面名称未判定"


def _build_validation_candidates(aspx_data: Dict[str, Any], codebehind_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    validations: List[Dict[str, Any]] = []

    for control in aspx_data.get("controls", []):
        if control.get("required"):
            validations.append({
                "target": control.get("id"),
                "check_type": "required",
                "detail": f'{control.get("label") or control.get("id")} は必須入力の可能性あり',
                "source": "aspx",
            })

        if control.get("maxlength"):
            validations.append({
                "target": control.get("id"),
                "check_type": "maxlength",
                "detail": f'maxlength={control.get("maxlength")}',
                "source": "aspx",
            })

    validations.extend(codebehind_data.get("validation_hints", []))
    return validations


def _build_screen_modes(aspx_data: Dict[str, Any], codebehind_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    modes: List[Dict[str, Any]] = []

    for control in aspx_data.get("controls", []):
        if control.get("id") == "hidReferenceMode":
            modes.append({
                "mode_name": "reference_mode",
                "detail": "画面上に参照モード用HiddenFieldあり",
                "source": "aspx",
            })

        css_class = control.get("css_class") or ""
        if "js-disable-in-ref" in css_class:
            modes.append({
                "mode_name": "reference_mode_disable_control",
                "detail": f'{control.get("id")} は参照モード時に非活性化対象の可能性あり',
                "source": "aspx",
            })

    modes.extend(codebehind_data.get("screen_mode_hints", []))
    return modes


def generate_analysis(
    aspx_data: Dict[str, Any],
    codebehind_data: Dict[str, Any],
    spec_data: Dict[str, Any],
) -> Dict[str, Any]:
    screen_id = _guess_screen_id(aspx_data)
    screen_name = _guess_screen_name(aspx_data)

    notes: List[str] = []

    if spec_data.get("raw_summary", {}).get("sheet_count", 0) == 0:
        notes.append("定義書は未読込、またはファイルが存在しません。")

    if aspx_data.get("raw_summary", {}).get("control_count", 0) == 0:
        notes.append("ASPXからコントロールを取得できませんでした。")

    return {
        "screen_id": screen_id,
        "screen_name": screen_name,
        "sources": {
            "aspx": aspx_data.get("file", ""),
            "codebehind": codebehind_data.get("file", ""),
            "spec": spec_data.get("file", ""),
        },
        "controls": aspx_data.get("controls", []),
        "events": codebehind_data.get("event_methods", []),
        "validations": _build_validation_candidates(aspx_data, codebehind_data),
        "screen_modes": _build_screen_modes(aspx_data, codebehind_data),
        "notes": notes,
        "table_headers": aspx_data.get("table_headers", []),
        "spec_summary": spec_data.get("raw_summary", {}),
    }