from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_CHECK_CONDITIONS: Dict[str, List[str]] = {
    "初期表示": ["通常モードで画面を起動する"],
    "入力項目": ["通常モードで画面を起動する"],
    "入力チェック": ["通常モードで画面を起動する"],
    "イベント": ["通常モードで画面を起動する"],
    "一覧表示": ["一覧表示対象データが存在する状態で画面を起動する"],
    "画面モード": ["参照モードで画面を起動する"],
    "排他制御": ["対象データが更新済みの状態で更新処理を実行する"],
}

DEFAULT_ACTIONS: Dict[str, List[str]] = {
    "初期表示": ["画面を起動する"],
    "入力項目": ["対象項目を確認する"],
    "入力チェック": ["対象項目に規定外の値を入力する"],
    "イベント": ["対象イベントを実行する"],
    "一覧表示": ["画面を起動する"],
    "画面モード": ["画面を起動する"],
    "排他制御": ["更新処理を実行する"],
}

DEFAULT_CONFIRMATIONS: Dict[str, List[str]] = {
    "初期表示": ["画面が正常に初期表示されること"],
    "入力項目": ["対象項目が入力可能であること"],
    "入力チェック": ["入力チェックが正しく行われること"],
    "イベント": ["イベント実行後の処理結果が正しいこと"],
    "一覧表示": ["一覧データが正しく表示されること"],
    "画面モード": ["参照モード時の制御が正しいこと"],
    "排他制御": ["排他制御が正しく行われること"],
}


EXPANSION_RULES: Dict[str, List[Dict[str, Any]]] = {
    "初期表示": [
        {
            "name_suffix": "（通常モード）",
            "pcl": ["N"],
            "check_conditions": ["通常モードで画面を起動する"],
            "actions": ["画面を起動する"],
        },
        {
            "name_suffix": "（参照モード）",
            "pcl": ["N"],
            "check_conditions": ["参照モードで画面を起動する"],
            "actions": ["画面を起動する"],
        },
    ],
    "一覧表示": [
        {
            "name_suffix": "（0件）",
            "pcl": ["N"],
            "check_conditions": ["一覧表示対象データが存在しない状態で画面を起動する"],
            "actions": ["画面を起動する"],
            "confirmation_suffix": ["一覧が0件で表示されること"],
        },
        {
            "name_suffix": "（1件）",
            "pcl": ["N"],
            "check_conditions": ["一覧表示対象データが1件存在する状態で画面を起動する"],
            "actions": ["画面を起動する"],
            "confirmation_suffix": ["一覧が1件で正しく表示されること"],
        },
        {
            "name_suffix": "（複数件）",
            "pcl": ["N"],
            "check_conditions": ["一覧表示対象データが複数件存在する状態で画面を起動する"],
            "actions": ["画面を起動する"],
            "confirmation_suffix": ["一覧が複数件で正しく表示されること"],
        },
        {
            "name_suffix": "（ソート）",
            "pcl": ["N"],
            "check_conditions": ["一覧表示対象データが複数件存在する状態で画面を起動する"],
            "actions": ["一覧のソート操作を実行する"],
            "confirmation_suffix": ["一覧が指定条件でソートされること"],
        },
    ],
    "画面モード": [
        {
            "name_suffix": "（通常モード）",
            "pcl": ["N"],
            "check_conditions": ["通常モードで画面を起動する"],
            "actions": ["画面を起動する"],
        },
        {
            "name_suffix": "（参照モード）",
            "pcl": ["N"],
            "check_conditions": ["参照モードで画面を起動する"],
            "actions": ["画面を起動する"],
        },
    ],
}


PCL_PRIORITY: Dict[str, int] = {
    "L": 1,
    "E": 2,
    "I": 3,
    "N": 4,
}


def _normalize_pcl(values: List[str]) -> List[str]:
    normalized_candidates: List[str] = []
    for value in values:
        pcl = str(value).strip().upper()
        if pcl in {"N", "E", "L", "I"}:
            normalized_candidates.append(pcl)

    unique_candidates = _unique_texts(normalized_candidates)
    if not unique_candidates:
        return ["N"]

    selected = min(unique_candidates, key=lambda item: PCL_PRIORITY.get(item, 99))
    return [selected]


def _merge_text_lists(base_values: List[str], extra_values: List[str]) -> List[str]:
    return _unique_texts(base_values + extra_values)


def _safe_to_int(value: Any) -> Optional[int]:
    try:
        if value is None or str(value).strip() == "":
            return None
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None



def _iter_candidate_field_lists(analysis: Dict[str, Any]) -> Iterable[List[Dict[str, Any]]]:
    candidate_keys = [
        "controls",
        "fields",
        "items",
        "input_items",
        "screen_items",
        "form_items",
    ]
    for key in candidate_keys:
        value = analysis.get(key)
        if isinstance(value, list):
            yield [item for item in value if isinstance(item, dict)]



def _collect_field_hints(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    hints: List[Dict[str, Any]] = []

    for items in _iter_candidate_field_lists(analysis):
        for item in items:
            label = str(
                item.get("label")
                or item.get("name")
                or item.get("item_name")
                or item.get("title")
                or item.get("id")
                or "対象項目"
            ).strip()
            control_id = str(item.get("id") or item.get("control_id") or "").strip()
            required = bool(item.get("required") or item.get("is_required") or item.get("mandatory"))
            max_length = _safe_to_int(
                item.get("max_length")
                or item.get("maxlength")
                or item.get("length")
                or item.get("digits")
            )
            min_length = _safe_to_int(
                item.get("min_length")
                or item.get("minlength")
            )
            data_type = str(
                item.get("data_type")
                or item.get("type")
                or item.get("input_type")
                or item.get("format")
                or ""
            ).strip().lower()
            charset = str(
                item.get("charset")
                or item.get("character_type")
                or item.get("zenhan")
                or ""
            ).strip().lower()

            hints.append(
                {
                    "label": label,
                    "control_id": control_id,
                    "required": required,
                    "max_length": max_length,
                    "min_length": min_length,
                    "data_type": data_type,
                    "charset": charset,
                }
            )

    return hints



def _match_field_hint(viewpoint: Dict[str, Any], field_hints: List[Dict[str, Any]]) -> Dict[str, Any]:
    title = str(viewpoint.get("title", "")).strip()
    details_text = " ".join([str(value) for value in viewpoint.get("details", [])])
    source_basis = " ".join([str(value) for value in viewpoint.get("source_basis", [])])
    search_text = f"{title} {details_text} {source_basis}"

    for hint in field_hints:
        label = str(hint.get("label", "")).strip()
        control_id = str(hint.get("control_id", "")).strip()
        if label and label in search_text:
            return hint
        if control_id and control_id in search_text:
            return hint

    return {
        "label": "対象項目",
        "control_id": "",
        "required": False,
        "max_length": None,
        "min_length": None,
        "data_type": "",
        "charset": "",
    }



def _is_numeric_field(field_hint: Dict[str, Any]) -> bool:
    data_type = str(field_hint.get("data_type", "")).lower()
    return any(keyword in data_type for keyword in ["number", "numeric", "digit", "int", "decimal", "num"])

def _is_blur_validation_viewpoint(viewpoint: Dict[str, Any]) -> bool:
    title = str(viewpoint.get("title", "")).strip()
    details_text = " ".join([str(value) for value in viewpoint.get("details", [])])
    source_basis_text = " ".join([str(value) for value in viewpoint.get("source_basis", [])])
    search_text = f"{title} {details_text} {source_basis_text}"
    return "フォーカスアウト時" in search_text or "blur_validation" in search_text or "common_frontend.blur_validation" in search_text


# --- Begin: Duplicate maxlength viewpoint helpers ---
def _extract_viewpoint_label(viewpoint: Dict[str, Any]) -> str:
    title = str(viewpoint.get("title", "")).strip()
    for suffix in [
        " の長さ制御確認",
        " のフォーカスアウト時桁数チェック確認",
        " の一覧表示確認",
        " のソート処理確認",
    ]:
        if suffix in title:
            return title.split(suffix, 1)[0].strip()
    return title


def _is_generic_length_viewpoint(viewpoint: Dict[str, Any]) -> bool:
    title = str(viewpoint.get("title", "")).strip()
    return " の長さ制御確認" in title


def _should_skip_duplicate_length_viewpoint(
    viewpoint: Dict[str, Any],
    all_viewpoints: List[Dict[str, Any]],
) -> bool:
    if not _is_generic_length_viewpoint(viewpoint):
        return False

    target_label = _extract_viewpoint_label(viewpoint)
    for other in all_viewpoints:
        if other is viewpoint:
            continue
        if not _is_blur_validation_viewpoint(other):
            continue
        if _extract_viewpoint_label(other) == target_label:
            return True

    return False
# --- End: Duplicate maxlength viewpoint helpers ---


# --- Begin: List display helpers ---
def _resolve_control_label_from_analysis(control_id: str, analysis: Dict[str, Any]) -> str:
    if not control_id:
        return ""

    for control in analysis.get("controls", []):
        cid = str(control.get("id", "")).strip()
        if cid != control_id:
            continue

        label = str(
            control.get("label")
            or control.get("name")
            or control.get("title")
            or ""
        ).strip()
        if label:
            return label

    return ""


# --- Begin: Button/action normalization helpers ---
def _collect_buttons(analysis: Dict[str, Any]) -> List[Dict[str, str]]:
    buttons: List[Dict[str, str]] = []
    seen_ids: set[str] = set()

    for control in analysis.get("controls", []):
        control_role = str(control.get("control_role", "")).strip()
        control_type = str(control.get("control_type") or control.get("type") or "").strip().lower()
        if control_role != "action" and control_type not in {"button", "linkbutton", "imagebutton"}:
            continue

        control_id = str(control.get("id") or "").strip()
        if control_id and control_id in seen_ids:
            continue
        if control_id:
            seen_ids.add(control_id)

        label = str(
            control.get("label")
            or control.get("text")
            or control.get("name")
            or control.get("title")
            or control_id
            or ""
        ).strip()

        if label:
            buttons.append(
                {
                    "id": control_id,
                    "label": label,
                }
            )

    return buttons
def _build_business_button_action(button_id: str, button_label: str, viewpoint: Dict[str, Any]) -> str:
    source_basis_text = " ".join([str(value) for value in viewpoint.get("source_basis", [])])
    title = str(viewpoint.get("title", "")).strip()
    details_text = " ".join([str(value) for value in viewpoint.get("details", [])])
    search_text = f"{title} {details_text} {source_basis_text}"

    if button_id == "btnClear" or "clear_customer_fields" in search_text or "顧客番号がクリア" in search_text:
        return "顧客クリアボタンを押下する"

    if button_id == "btnSummaryClear" or "clear_summary_fields" in search_text or "テキストエリアクリア" in title:
        return "概況クリアボタンを押下する"

    if button_id == "btnCustSearch" or "customer_search" in search_text or "顧客検索" in search_text:
        return "顧客検索ボタンを押下する"

    if button_id == "btnDownload" or "js.click.download" in search_text or "ダウンロード" in search_text:
        return "帳票ダウンロードボタンを押下する"

    return f"{button_label}ボタンを押下する"



def _select_button_for_action(
    action_text: str,
    viewpoint: Dict[str, Any],
    analysis: Dict[str, Any],
) -> Dict[str, str]:
    buttons = _collect_buttons(analysis)
    if not buttons:
        return {}

    title = str(viewpoint.get("title", "")).strip()
    details_text = " ".join([str(value) for value in viewpoint.get("details", [])])
    source_basis_values = [str(value) for value in viewpoint.get("source_basis", [])]
    source_basis_text = " ".join(source_basis_values)
    search_text = f"{action_text} {title} {details_text} {source_basis_text}"

    # 1) source_basis に controls.<id> があれば最優先
    for source in source_basis_values:
        if source.startswith("controls."):
            target_id = source.replace("controls.", "").strip()
            for button in buttons:
                if button.get("id") == target_id:
                    return button

    keyword_priority: List[Tuple[str, List[str]]] = [
        ("登録", ["登録", "更新", "保存", "確定"]),
        ("更新", ["更新", "保存", "登録"]),
        ("検索", ["検索", "顧客表示", "表示"]),
        ("削除", ["削除"]),
        ("クリア", ["クリア"]),
        ("ダウンロード", ["ダウンロード", "出力", "印刷"]),
        ("追加", ["追加", "新規"]),
    ]

    matched_keywords: List[str] = []
    for trigger_word, candidates in keyword_priority:
        if trigger_word in search_text:
            matched_keywords.extend(candidates)

    for keyword in matched_keywords:
        for button in buttons:
            if keyword in button.get("label", ""):
                return button

    for button in buttons:
        if button.get("label", "") in search_text:
            return button
        if button.get("id", "") and button.get("id", "") in search_text:
            return button

    if len(buttons) == 1:
        return buttons[0]

    for fallback in ["登録", "更新", "保存", "検索", "クリア", "ダウンロード"]:
        for button in buttons:
            if fallback in button.get("label", ""):
                return button

    return {}



def _normalize_action_text(action_text: str, viewpoint: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    text = str(action_text).strip()
    if not text:
        return text

    generic_action_markers = [
        "更新処理を実行する",
        "登録処理を実行する",
        "検索処理を実行する",
        "削除処理を実行する",
        "クリア処理を実行する",
        "ダウンロード処理を実行する",
        "対象イベントを実行する",
    ]

    if not any(marker in text for marker in generic_action_markers):
        return text

    button = _select_button_for_action(text, viewpoint, analysis)
    if button:
        return _build_business_button_action(
            button.get("id", ""),
            button.get("label", ""),
            viewpoint,
        )

    return text
# --- End: Button/action normalization helpers ---


def _extract_list_label_from_viewpoint(viewpoint: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    title = str(viewpoint.get("title", "")).strip()
    source_basis = [str(value) for value in viewpoint.get("source_basis", [])]

    if " の一覧表示確認" in title:
        candidate = title.split(" の一覧表示確認", 1)[0].strip()
        resolved = _resolve_control_label_from_analysis(candidate, analysis)
        if resolved:
            return resolved
        if candidate:
            return candidate

    for value in source_basis:
        if value.startswith("table_headers."):
            candidate = value.replace("table_headers.", "").strip()
            resolved = _resolve_control_label_from_analysis(candidate, analysis)
            if resolved:
                return resolved
            if candidate:
                return candidate

        if value.startswith("controls."):
            candidate = value.replace("controls.", "").strip()
            resolved = _resolve_control_label_from_analysis(candidate, analysis)
            if resolved:
                return resolved
            if candidate:
                return candidate

    for value in source_basis:
        resolved = _resolve_control_label_from_analysis(value, analysis)
        if resolved:
            return resolved

    return "一覧"
# --- End: List display helpers ---

def _build_blur_validation_expansion_rules(viewpoint: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    field_hint = _match_field_hint(viewpoint, _collect_field_hints(analysis))
    label = str(field_hint.get("label", "対象項目")).strip() or "対象項目"
    max_length = field_hint.get("max_length")

    if label == "対象項目":
        return [
            {
                "name_suffix": "（最大桁数以内）",
                "pcl": ["N"],
                "check_conditions": ["対象項目に最大桁数以内の値を入力する"],
                "actions": ["他項目へフォーカスを移動する"],
                "confirmation_suffix": ["エラーメッセージが表示されないこと"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（最大桁数超過）",
                "pcl": ["L"],
                "check_conditions": ["対象項目に最大桁数超過の値を入力する"],
                "actions": ["他項目へフォーカスを移動する"],
                "confirmation_suffix": ["エラーメッセージが表示されること"],
                "replace_base_confirmations": True,
            },
        ]

    rules: List[Dict[str, Any]] = [
        {
            "name_suffix": "（最大桁数以内）",
            "pcl": ["N"],
            "check_conditions": [f"{label}に最大桁数以内の値を入力する"],
            "actions": [f"{label}入力欄でフォーカスアウトする"],
            "confirmation_suffix": ["エラーメッセージが表示されないこと"],
            "replace_base_confirmations": True,
        }
    ]

    if max_length is not None and max_length > 0:
        rules.append(
            {
                "name_suffix": "（最大桁数ちょうど）",
                "pcl": ["L"],
                "check_conditions": [f"{label}に最大桁数ちょうどの値を入力する"],
                "actions": [f"{label}入力欄でフォーカスアウトする"],
                "confirmation_suffix": ["エラーメッセージが表示されないこと"],
                "replace_base_confirmations": True,
            }
        )
        rules.append(
            {
                "name_suffix": "（最大桁数超過）",
                "pcl": ["L"],
                "check_conditions": [f"{label}に最大桁数超過の値を入力する"],
                "actions": [f"{label}入力欄でフォーカスアウトする"],
                "confirmation_suffix": ["エラーメッセージが表示されること"],
                "replace_base_confirmations": True,
            }
        )

    return rules


# --- Begin: List display expansion rule builder ---
# --- Begin: List display expansion rule builder ---
def _build_list_display_expansion_rules(viewpoint: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    list_label = _extract_list_label_from_viewpoint(viewpoint, analysis)

    if not list_label.endswith("一覧"):
        list_label = f"{list_label}一覧"

    return [
        {
            "name_suffix": "（0件）",
            "pcl": ["N"],
            "check_conditions": [f"{list_label}の表示対象データが存在しない状態で画面を起動する"],
            "actions": ["画面を起動する"],
            "confirmation_suffix": [f"{list_label}が0件で表示されること"],
        },
        {
            "name_suffix": "（1件）",
            "pcl": ["N"],
            "check_conditions": [f"{list_label}の表示対象データが1件存在する状態で画面を起動する"],
            "actions": ["画面を起動する"],
            "confirmation_suffix": [f"{list_label}が1件で正しく表示されること"],
        },
        {
            "name_suffix": "（複数件）",
            "pcl": ["N"],
            "check_conditions": [f"{list_label}の表示対象データが複数件存在する状態で画面を起動する"],
            "actions": ["画面を起動する"],
            "confirmation_suffix": [f"{list_label}が複数件で正しく表示されること"],
        },
        {
            "name_suffix": "（ソート）",
            "pcl": ["N"],
            "check_conditions": [f"{list_label}の表示対象データが複数件存在する状態で画面を起動する"],
            "actions": [f"{list_label}のソート操作を実行する"],
            "confirmation_suffix": [f"{list_label}が指定条件でソートされること"],
        },
    ]


def _build_javascript_event_expansion_rules(viewpoint: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    title = str(viewpoint.get("title", "")).strip()
    source_basis_text = " ".join([str(value) for value in viewpoint.get("source_basis", [])])
    search_text = f"{title} {source_basis_text}"

    if "顧客クリアボタン押下時の項目クリア確認" in title or "controls.btnClear" in search_text:
        return [
            {
                "name_suffix": "（顧客番号）",
                "pcl": ["N"],
                "actions": ["顧客クリアボタンを押下する"],
                "confirmation_suffix": ["顧客番号がクリアされること"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（顧客名）",
                "pcl": ["N"],
                "actions": ["顧客クリアボタンを押下する"],
                "confirmation_suffix": ["顧客名がクリアされること"],
                "replace_base_confirmations": True,
            },
        ]

    if "概況クリアボタン押下時のテキストエリアクリア確認" in title or "controls.btnSummaryClear" in search_text:
        return [
            {
                "name_suffix": "（事故原因）",
                "pcl": ["N"],
                "actions": ["概況クリアボタンを押下する"],
                "confirmation_suffix": ["事故及び延滞に至った原因がクリアされること"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（現況）",
                "pcl": ["N"],
                "actions": ["概況クリアボタンを押下する"],
                "confirmation_suffix": ["債務者および保証人の現況がクリアされること"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（方針）",
                "pcl": ["N"],
                "actions": ["概況クリアボタンを押下する"],
                "confirmation_suffix": ["回収、解消の方針、スケジュールがクリアされること"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（備考）",
                "pcl": ["N"],
                "actions": ["概況クリアボタンを押下する"],
                "confirmation_suffix": ["備考、特記事項がクリアされること"],
                "replace_base_confirmations": True,
            },
        ]

    if "顧客検索ボタン押下時の前提条件・検索結果反映確認" in title or "controls.btnCustSearch" in search_text:
        return [
            {
                "name_suffix": "（店番未選択）",
                "pcl": ["E"],
                "actions": ["顧客検索ボタンを押下する"],
                "confirmation_suffix": ["店番未選択の場合はエラーメッセージが表示されること"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（正常起動）",
                "pcl": ["N"],
                "actions": ["顧客検索ボタンを押下する"],
                "confirmation_suffix": ["顧客検索ダイアログが起動すること"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（反映）",
                "pcl": ["N"],
                "actions": ["顧客検索ボタンを押下し、顧客を選択する"],
                "confirmation_suffix": ["顧客番号および顧客名が画面へ反映されること"],
                "replace_base_confirmations": True,
            },
        ]

    if "帳票ダウンロードボタン押下時の前提条件確認" in title or "controls.btnDownload" in search_text:
        return [
            {
                "name_suffix": "（顧客番号未入力）",
                "pcl": ["E"],
                "actions": ["帳票ダウンロードボタンを押下する"],
                "confirmation_suffix": ["顧客番号未入力の場合はエラーメッセージが表示されること"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（店番未選択）",
                "pcl": ["E"],
                "actions": ["帳票ダウンロードボタンを押下する"],
                "confirmation_suffix": ["店番未選択の場合はエラーメッセージが表示されること"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（帳票未選択）",
                "pcl": ["E"],
                "actions": ["帳票ダウンロードボタンを押下する"],
                "confirmation_suffix": ["帳票未選択の場合はエラーメッセージが表示されること"],
                "replace_base_confirmations": True,
            },
            {
                "name_suffix": "（正常）",
                "pcl": ["N"],
                "actions": ["帳票ダウンロードボタンを押下する"],
                "confirmation_suffix": ["正常時はダウンロード処理が実行されること"],
                "replace_base_confirmations": True,
            },
        ]

    return []

def _build_input_check_expansion_rules(viewpoint: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    field_hint = _match_field_hint(viewpoint, _collect_field_hints(analysis))
    label = str(field_hint.get("label", "対象項目")).strip() or "対象項目"
    max_length = field_hint.get("max_length")
    min_length = field_hint.get("min_length")
    required = bool(field_hint.get("required"))
    charset = str(field_hint.get("charset", "")).lower()

    if label == "対象項目":
        return [
            {
                "name_suffix": "（正常系）",
                "pcl": ["N"],
                "actions": ["対象操作を実行する"],
                "confirmation_suffix": ["想定した処理結果となること"],
            },
            {
                "name_suffix": "（入力不足）",
                "pcl": ["E"],
                "actions": ["必須条件を満たさない状態で操作する"],
                "confirmation_suffix": ["エラーメッセージが表示されること"],
            },
        ]


    rules: List[Dict[str, Any]] = [
        {
            "name_suffix": "（正常値）",
            "pcl": ["N"],
            "actions": [f"{label}に正常値を入力する"],
            "confirmation_suffix": [f"{label}に正常値を入力した場合、エラーとならないこと"],
        }
    ]

    if required:
        rules.append(
            {
                "name_suffix": "（空白）",
                "pcl": ["E"],
                "actions": [f"{label}を空白で入力する"],
                "confirmation_suffix": [f"{label}を空白で入力した場合、エラーメッセージが表示されること"],
            }
        )

    if min_length is not None and min_length > 0:
        rules.append(
            {
                "name_suffix": "（下限未満）",
                "pcl": ["L"],
                "actions": [f"{label}に下限未満の値を入力する"],
                "confirmation_suffix": [f"{label}に下限未満の値を入力した場合、境界値チェック結果が正しいこと"],
            }
        )

    if max_length is not None and max_length > 0:
        rules.append(
            {
                "name_suffix": "（上限値）",
                "pcl": ["L"],
                "actions": [f"{label}に上限値を入力する"],
                "confirmation_suffix": [f"{label}に上限値を入力した場合、境界値チェック結果が正しいこと"],
            }
        )
        rules.append(
            {
                "name_suffix": "（上限超過）",
                "pcl": ["L"],
                "actions": [f"{label}に上限超過の値を入力する"],
                "confirmation_suffix": [f"{label}に上限超過の値を入力した場合、境界値チェック結果が正しいこと"],
            }
        )

    if _is_numeric_field(field_hint):
        rules.append(
            {
                "name_suffix": "（数字以外）",
                "pcl": ["E"],
                "actions": [f"{label}に数字以外の値を入力する"],
                "confirmation_suffix": [f"{label}に数字以外の値を入力した場合、エラーメッセージが表示されること"],
            }
        )

    if "zen" in charset or "全角" in charset:
        rules.append(
            {
                "name_suffix": "（半角入力）",
                "pcl": ["E"],
                "actions": [f"{label}に半角で入力する"],
                "confirmation_suffix": [f"{label}に半角で入力した場合、入力チェック結果が正しいこと"],
            }
        )
    elif "han" in charset or "half" in charset or "半角" in charset:
        rules.append(
            {
                "name_suffix": "（全角入力）",
                "pcl": ["E"],
                "actions": [f"{label}に全角で入力する"],
                "confirmation_suffix": [f"{label}に全角で入力した場合、入力チェック結果が正しいこと"],
            }
        )

    return rules


def _unique_texts(values: List[str]) -> List[str]:
    seen = set()
    results: List[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        results.append(text)
    return results


def _next_definition_id(prefix: str, index: int) -> str:
    return f"{prefix}-{index:03d}"


def _register_definition(
    registry: Dict[str, str],
    definitions: List[Dict[str, str]],
    prefix: str,
    text: str,
) -> str:
    normalized = text.strip()
    if normalized in registry:
        return registry[normalized]

    definition_id = _next_definition_id(prefix, len(definitions) + 1)
    registry[normalized] = definition_id
    definitions.append({"id": definition_id, "text": normalized})
    return definition_id


def _build_case_items(
    viewpoint: Dict[str, Any],
    analysis: Dict[str, Any],
    expansion_rule: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[str], List[str]]:
    category = str(viewpoint.get("category", "")).strip()
    details = viewpoint.get("details", [])
    detail_texts = _unique_texts([str(detail) for detail in details])

    base_check_conditions = _unique_texts(
        [str(value) for value in DEFAULT_CHECK_CONDITIONS.get(category, ["画面を起動する"])]
    )
    base_actions = _unique_texts(
        [_normalize_action_text(str(value), viewpoint, analysis) for value in DEFAULT_ACTIONS.get(category, ["対象処理を実行する"])]
    )
    base_confirmations = _unique_texts(
        detail_texts or DEFAULT_CONFIRMATIONS.get(category, ["期待結果が正しいこと"])
    )

    if expansion_rule is None:
        return base_check_conditions, base_actions, base_confirmations

    check_conditions = _merge_text_lists(
        [str(value) for value in expansion_rule.get("check_conditions", [])],
        [],
    ) or base_check_conditions
    actions = _merge_text_lists(
        [_normalize_action_text(str(value), viewpoint, analysis) for value in expansion_rule.get("actions", [])],
        [],
    ) or base_actions
    confirmation_suffixes = [str(value) for value in expansion_rule.get("confirmation_suffix", [])]
    if expansion_rule.get("replace_base_confirmations"):
        confirmations = _unique_texts(confirmation_suffixes)
    else:
        confirmations = _merge_text_lists(
            base_confirmations,
            confirmation_suffixes,
        )

    return check_conditions, actions, confirmations


def _expand_viewpoint(viewpoint: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    category = str(viewpoint.get("category", "")).strip()
    title = str(viewpoint.get("title", "")).strip()
    viewpoint_pcl = _normalize_pcl([str(value) for value in viewpoint.get("pcl", [])])
    if category == "入力チェック" and _is_blur_validation_viewpoint(viewpoint):
        rules = _build_blur_validation_expansion_rules(viewpoint, analysis)
    elif category == "入力チェック":
        rules = _build_input_check_expansion_rules(viewpoint, analysis)
    elif category == "一覧表示":
        rules = _build_list_display_expansion_rules(viewpoint, analysis)
    elif category == "イベント":
        rules = _build_javascript_event_expansion_rules(viewpoint, analysis) or EXPANSION_RULES.get(category)
    else:
        rules = EXPANSION_RULES.get(category)

    if not rules:
        return [
            {
                "title": title,
                "pcl": viewpoint_pcl,
                "rule": None,
            }
        ]

    expanded_cases: List[Dict[str, Any]] = []
    for rule in rules:
        expanded_cases.append(
            {
                "title": f"{title}{str(rule.get('name_suffix', '')).strip()}",
                "pcl": _normalize_pcl([str(value) for value in rule.get("pcl", [])]) or viewpoint_pcl,
                "rule": rule,
            }
        )

    return expanded_cases


def _build_testcase_from_viewpoint(
    viewpoint: Dict[str, Any],
    expanded_case: Dict[str, Any],
    analysis: Dict[str, Any],
    index: int,
    check_condition_registry: Dict[str, str],
    check_condition_definitions: List[Dict[str, str]],
    action_registry: Dict[str, str],
    action_definitions: List[Dict[str, str]],
    confirmation_registry: Dict[str, str],
    confirmation_definitions: List[Dict[str, str]],
) -> Dict[str, Any]:
    case_id = f"TC-{index:03d}"
    case_no = f"{index:04d}"
    category = str(viewpoint.get("category", "")).strip()
    viewpoint_id = str(viewpoint.get("id", "")).strip()
    viewpoint_title = str(expanded_case.get("title", viewpoint.get("title", ""))).strip()
    source_basis = _unique_texts([viewpoint_id] + [str(value) for value in viewpoint.get("source_basis", [])])
    pcl = _normalize_pcl([str(value) for value in expanded_case.get("pcl", [])])

    check_conditions, actions, confirmations = _build_case_items(
        viewpoint,
        analysis,
        expansion_rule=expanded_case.get("rule"),
    )

    check_condition_ids = [
        _register_definition(
            check_condition_registry,
            check_condition_definitions,
            "C",
            text,
        )
        for text in check_conditions
    ]
    action_ids = [
        _register_definition(
            action_registry,
            action_definitions,
            "A",
            text,
        )
        for text in actions
    ]
    confirmation_ids = [
        _register_definition(
            confirmation_registry,
            confirmation_definitions,
            "E",
            text,
        )
        for text in confirmations
    ]

    return {
        "case_id": case_id,
        "case_no": case_no,
        "category": category,
        "test_viewpoint_id": viewpoint_id,
        "test_viewpoint": viewpoint_title,
        "pcl": pcl,
        "check_condition_ids": check_condition_ids,
        "action_ids": action_ids,
        "confirmation_ids": confirmation_ids,
        "source_basis": source_basis,
    }


def generate_testcases(
    analysis: Dict[str, Any],
    viewpoints: Dict[str, Any],
) -> Dict[str, Any]:
    test_cases: List[Dict[str, Any]] = []

    check_condition_registry: Dict[str, str] = {}
    check_condition_definitions: List[Dict[str, str]] = []
    action_registry: Dict[str, str] = {}
    action_definitions: List[Dict[str, str]] = []
    confirmation_registry: Dict[str, str] = {}
    confirmation_definitions: List[Dict[str, str]] = []

    case_index = 1
    all_viewpoints = viewpoints.get("viewpoints", [])
    for viewpoint in all_viewpoints:
        if _should_skip_duplicate_length_viewpoint(viewpoint, all_viewpoints):
            continue

        expanded_cases = _expand_viewpoint(viewpoint, analysis)
        for expanded_case in expanded_cases:
            test_cases.append(
                _build_testcase_from_viewpoint(
                    viewpoint=viewpoint,
                    expanded_case=expanded_case,
                    analysis=analysis,
                    index=case_index,
                    check_condition_registry=check_condition_registry,
                    check_condition_definitions=check_condition_definitions,
                    action_registry=action_registry,
                    action_definitions=action_definitions,
                    confirmation_registry=confirmation_registry,
                    confirmation_definitions=confirmation_definitions,
                )
            )
            case_index += 1

    return {
        "screen_id": analysis.get("screen_id"),
        "screen_name": analysis.get("screen_name"),
        "definitions": {
            "check_conditions": check_condition_definitions,
            "actions": action_definitions,
            "confirmations": confirmation_definitions,
        },
        "test_cases": test_cases,
        "summary": {
            "test_case_count": len(test_cases),
            "source_viewpoint_count": len(viewpoints.get("viewpoints", [])),
            "check_condition_count": len(check_condition_definitions),
            "action_count": len(action_definitions),
            "confirmation_count": len(confirmation_definitions),
            "pcl_assigned_case_count": sum(1 for case in test_cases if case.get("pcl")),
            "analysis_linked_field_count": len(_collect_field_hints(analysis)),
        },
    }