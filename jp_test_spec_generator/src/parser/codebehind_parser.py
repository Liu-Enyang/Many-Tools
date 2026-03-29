from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List


METHOD_PATTERN = re.compile(
    r'(?:protected|private|public)\s+void\s+([A-Za-z0-9_]+)\s*\(',
    re.MULTILINE
)


def _infer_event_type(method_name: str) -> str:
    lower = method_name.lower()
    if lower == "page_load":
        return "PageLoad"
    if lower.endswith("_click"):
        return "Click"
    if lower.endswith("_selectedindexchanged"):
        return "SelectedIndexChanged"
    if lower.endswith("_itemcommand"):
        return "ItemCommand"
    return "Method"


def _extract_methods(content: str) -> List[Dict[str, Any]]:
    methods: List[Dict[str, Any]] = []
    for match in METHOD_PATTERN.finditer(content):
        name = match.group(1)
        methods.append({
            "name": name,
            "event_type": _infer_event_type(name),
            "related_controls": [],
        })
    return methods


def _extract_validation_hints(content: str) -> List[Dict[str, Any]]:
    hints: List[Dict[str, Any]] = []

    if "Length" in content or "length" in content or "MaxLength" in content:
        hints.append({
            "check_type": "length_check_hint",
            "target": None,
            "detail": "コードビハインド内に桁数・長さチェックの可能性あり",
            "source": "codebehind",
        })

    if "message" in content.lower() or "Message" in content:
        hints.append({
            "check_type": "message_output_hint",
            "target": None,
            "detail": "メッセージエリア出力処理の可能性あり",
            "source": "codebehind",
        })

    if "UpdateDateTime" in content or "hidUpdateDateTime" in content:
        hints.append({
            "check_type": "concurrency_check_hint",
            "target": "hidUpdateDateTime",
            "detail": "排他チェックの可能性あり",
            "source": "codebehind",
        })

    return hints


def _extract_screen_mode_hints(content: str) -> List[Dict[str, Any]]:
    hints: List[Dict[str, Any]] = []

    if "QueryString" in content:
        hints.append({
            "mode_name": "reference_mode_hint",
            "detail": "QueryStringを利用した画面モード分岐の可能性あり",
            "source": "codebehind",
        })

    if "Enabled = false" in content or ".Enabled=false" in content.replace(" ", ""):
        hints.append({
            "mode_name": "disable_control_hint",
            "detail": "条件によりコントロール非活性化処理の可能性あり",
            "source": "codebehind",
        })

    if "Visible = false" in content or ".Visible=false" in content.replace(" ", ""):
        hints.append({
            "mode_name": "hide_control_hint",
            "detail": "条件によりコントロール非表示化処理の可能性あり",
            "source": "codebehind",
        })

    if "!IsPostBack" in content.replace(" ", "") or "if(!IsPostBack)" in content.replace(" ", ""):
        hints.append({
            "mode_name": "initial_display_hint",
            "detail": "初期表示処理あり",
            "source": "codebehind",
        })

    return hints


def parse_codebehind(file_path: str | Path) -> Dict[str, Any]:
    path = Path(file_path)
    content = path.read_text(encoding="utf-8", errors="ignore")

    return {
        "file": str(path),
        "event_methods": _extract_methods(content),
        "validation_hints": _extract_validation_hints(content),
        "screen_mode_hints": _extract_screen_mode_hints(content),
        "raw_summary": {
            "method_count": len(_extract_methods(content)),
        },
    }