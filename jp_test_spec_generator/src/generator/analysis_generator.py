from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


TITLE_CSS_CANDIDATES = {
    "title",
    "page-title",
    "screen-title",
    "main-title",
}

HIDDEN_NON_TEST_TARGET_IDS = {
    "hidmode",
    "hidreferencemode",
    "hidkind",
    "hiddefinition",
    "hidaction",
    "hidcheck",
}

NON_TEST_TARGET_CONTROL_IDS = {
    "dummy",
}


def _guess_screen_id(aspx_data: Dict[str, Any]) -> str:
    file_name = Path(aspx_data.get("file", "")).stem
    return file_name or "UnknownScreen"


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _guess_screen_name(aspx_data: Dict[str, Any], spec_data: Dict[str, Any]) -> str:
    title_candidates = aspx_data.get("title_candidates", [])
    for candidate in title_candidates:
        text = _clean_text(candidate.get("text"))
        css_class = _clean_text(candidate.get("css_class")).lower()
        if text and css_class in TITLE_CSS_CANDIDATES:
            return text

    for candidate in title_candidates:
        text = _clean_text(candidate.get("text"))
        if text:
            return text

    for control in aspx_data.get("controls", []):
        if control.get("type") == "Label" and control.get("text"):
            return control["text"]

    for sheet in spec_data.get("sheets", []):
        for row in sheet.get("rows", []):
            row_text = " ".join(_clean_text(cell) for cell in row if cell is not None)
            if "画面名" in row_text or "画面名称" in row_text:
                values = [_clean_text(cell) for cell in row if _clean_text(cell)]
                if values:
                    return values[-1]

    file_name = Path(aspx_data.get("file", "")).stem
    return file_name or "画面名称未判定"


def _infer_control_role(control: Dict[str, Any]) -> str:
    control_type = _clean_text(control.get("type"))

    if control_type in {"TextBox", "DropDownList", "RadioButtonList", "CheckBox"}:
        return "input"
    if control_type in {"Button", "LinkButton", "HtmlButton"}:
        return "action"
    if control_type == "Label":
        return "display"
    if control_type == "HiddenField":
        return "hidden"
    if control_type == "Repeater":
        return "list"
    return "other"


def _infer_test_target(control: Dict[str, Any], control_role: str) -> bool:
    control_id = _clean_text(control.get("id")).lower()

    if control_id in NON_TEST_TARGET_CONTROL_IDS:
        return False

    if control_role == "hidden":
        return control_id == "hidupdatedatetime"

    if control_id in HIDDEN_NON_TEST_TARGET_IDS:
        return False

    return control_role in {"input", "action", "display", "list"}


def _decorate_controls(aspx_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    decorated: List[Dict[str, Any]] = []

    for control in aspx_data.get("controls", []):
        copied = dict(control)
        control_role = _infer_control_role(copied)
        copied["control_role"] = control_role
        copied["test_target"] = _infer_test_target(copied, control_role)
        copied["source_basis"] = ["aspx"]

        copied["required_ui_hint"] = bool(copied.get("required"))
        copied["required_business"] = None

        maxlength = copied.get("maxlength")
        blur_validation_rules: List[Dict[str, Any]] = []
        if maxlength:
            blur_validation_rules.append({
                "rule_type": "maxlength_blur_check",
                "max_length": maxlength,
                "trigger": "blur",
                "implemented_by": "common_frontend",
                "detail": f"maxlength={maxlength} の項目はフォーカスアウト時に桁数チェック対象とみなす",
                "source_basis": ["aspx.maxlength", "common_frontend.blur_validation"],
            })

        copied["input_rule"] = {
            "html_maxlength": maxlength,
            "business_rule": None,
            "blur_validation_rules": blur_validation_rules,
        }

        decorated.append(copied)

    return decorated


def _build_validation_candidates(
    controls: List[Dict[str, Any]],
    codebehind_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    validations: List[Dict[str, Any]] = []

    for control in controls:
        if control.get("required_ui_hint"):
            validations.append({
                "target": control.get("id"),
                "check_type": "required_ui_hint",
                "detail": f'{control.get("label") or control.get("id")} に required 属性あり',
                "source": "aspx",
                "source_basis": ["aspx.required"],
            })

        if control.get("maxlength"):
            validations.append({
                "target": control.get("id"),
                "check_type": "maxlength",
                "detail": f'maxlength={control.get("maxlength")} のため、フォーカスアウト時の桁数チェック対象',
                "source": "aspx",
                "trigger": "blur",
                "implemented_by": "common_frontend",
                "max_length": control.get("maxlength"),
                "source_basis": ["aspx.maxlength", "common_frontend.blur_validation"],
            })

    for hint in codebehind_data.get("validation_hints", []):
        copied = dict(hint)
        copied.setdefault("source_basis", ["codebehind"])
        validations.append(copied)

    return validations


def _categorize_events(codebehind_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    result = {
        "user_actions": [],
        "lifecycle": [],
        "internal_methods": [],
    }

    for event in codebehind_data.get("event_methods", []):
        copied = dict(event)
        copied["source_basis"] = ["codebehind"]
        event_type = _clean_text(copied.get("event_type"))
        name = _clean_text(copied.get("name")).lower()

        if event_type in {"Click", "SelectedIndexChanged", "ItemCommand"}:
            result["user_actions"].append(copied)
        elif event_type == "PageLoad" or name in {"oninit", "initializecomponent"}:
            result["lifecycle"].append(copied)
        else:
            result["internal_methods"].append(copied)

    return result


def _build_screen_modes(
    controls: List[Dict[str, Any]],
    codebehind_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    modes: List[Dict[str, Any]] = []

    disable_controls: List[str] = []
    has_reference_mode_flag = False

    for control in controls:
        control_id = _clean_text(control.get("id"))
        if control_id == "hidReferenceMode":
            has_reference_mode_flag = True

        css_class = _clean_text(control.get("css_class"))
        if "js-disable-in-ref" in css_class:
            disable_controls.append(control_id)

    screen_mode_hints = codebehind_data.get("screen_mode_hints", [])
    has_querystring_hint = any("QueryString" in _clean_text(hint.get("detail")) for hint in screen_mode_hints)
    has_initial_display_hint = any("初期表示" in _clean_text(hint.get("detail")) for hint in screen_mode_hints)

    if has_reference_mode_flag or has_querystring_hint or disable_controls:
        modes.append({
            "mode_name": "reference_mode",
            "trigger": [
                trigger
                for trigger in [
                    "hidReferenceMode" if has_reference_mode_flag else None,
                    "QueryString" if has_querystring_hint else None,
                ]
                if trigger
            ],
            "effects": {
                "disable_controls": sorted(set(disable_controls)),
            },
            "source": ["aspx", "codebehind"],
            "source_basis": ["hidReferenceMode", "js-disable-in-ref", "QueryString hint"],
        })

    if has_initial_display_hint:
        modes.append({
            "mode_name": "initial_display",
            "trigger": ["!IsPostBack"],
            "effects": {
                "notes": ["初期表示処理あり"],
            },
            "source": ["codebehind"],
            "source_basis": ["!IsPostBack"],
        })

    return modes


def build_javascript_analysis(javascript_sources: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    result: Dict[str, List[Dict[str, Any]]] = {
        "event_handlers": [],
        "screen_controls": [],
        "validation_related": [],
        "download_related": [],
        "sort_related": [],
    }

    for src in javascript_sources:
        path = _clean_text(src.get("relative_path"))
        file_name = _clean_text(src.get("file_name"))
        content = _clean_text(src.get("content"))

        def add(target_key: str, title: str, detail: str) -> None:
            result[target_key].append(
                {
                    "file_name": file_name,
                    "relative_path": path,
                    "title": title,
                    "detail": detail,
                    "source_basis": [path or file_name or "javascript"],
                }
            )

        if "addEventListener('click'" in content or 'addEventListener("click"' in content:
            add("event_handlers", "クリックイベント制御あり", "ボタン押下時のフロント処理を実装している")

        if (
            "applyReferenceMode" in content
            or "disabled = true" in content
            or "pointerEvents = 'none'" in content
            or 'pointerEvents = "none"' in content
        ):
            add("screen_controls", "参照モード制御あり", "参照モード時に入力・ボタン・リンクを操作不可にする制御がある")

        if "showError(" in content or "alert(" in content:
            add("validation_related", "前端エラーメッセージ制御あり", "入力不足や選択不足時にエラーメッセージを表示する制御がある")

        if "DownLoadRSheet.aspx" in content or "downloadFrame" in content or "btnDownload" in content:
            add("download_related", "帳票ダウンロード制御あり", "帳票選択チェック・顧客番号/店番チェック・ダウンロード実行の制御がある")

        if "initSort(" in content or "sortTable(" in content or "data-sort" in content:
            add("sort_related", "一覧ソート制御あり", "一覧ヘッダクリックによる昇順/降順ソート制御がある")

    return result


def generate_analysis(
    aspx_data: Dict[str, Any],
    codebehind_data: Dict[str, Any],
    spec_data: Dict[str, Any],
    javascript_sources: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    screen_id = _guess_screen_id(aspx_data)
    screen_name = _guess_screen_name(aspx_data, spec_data)
    controls = _decorate_controls(aspx_data)
    javascript_sources = javascript_sources or []
    javascript_analysis = build_javascript_analysis(javascript_sources)

    notes: List[str] = []

    if spec_data.get("raw_summary", {}).get("sheet_count", 0) == 0:
        notes.append("定義書は未読込、またはファイルが存在しません。")

    if aspx_data.get("raw_summary", {}).get("control_count", 0) == 0:
        notes.append("ASPXからコントロールを取得できませんでした。")

    if javascript_sources and not any(javascript_analysis.values()):
        notes.append("JavaScriptファイルは読み込みましたが、テスト観点に使える前端制御は抽出できませんでした。")

    return {
        "screen_id": screen_id,
        "screen_name": screen_name,
        "sources": {
            "aspx": aspx_data.get("file", ""),
            "codebehind": codebehind_data.get("file", ""),
            "spec": spec_data.get("file", ""),
        },
        "controls": controls,
        "events": _categorize_events(codebehind_data),
        "validations": _build_validation_candidates(controls, codebehind_data),
        "blur_validation_targets": [
            {
                "target": control.get("id"),
                "label": control.get("label") or control.get("id"),
                "max_length": control.get("maxlength"),
                "trigger": "blur",
                "implemented_by": "common_frontend",
                "source_basis": ["aspx.maxlength", "common_frontend.blur_validation"],
            }
            for control in controls
            if control.get("maxlength")
        ],
        "screen_modes": _build_screen_modes(controls, codebehind_data),
        "javascript_sources": javascript_sources,
        "javascript_analysis": javascript_analysis,
        "notes": notes,
        "table_headers": aspx_data.get("table_headers", []),
        "title_candidates": aspx_data.get("title_candidates", []),
        "spec_summary": spec_data.get("raw_summary", {}),
    }