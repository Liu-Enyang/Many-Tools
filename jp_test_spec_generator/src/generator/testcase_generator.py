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
    expansion_rule: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[str], List[str]]:
    category = str(viewpoint.get("category", "")).strip()
    details = viewpoint.get("details", [])
    detail_texts = _unique_texts([str(detail) for detail in details])

    base_check_conditions = _unique_texts(
        [str(value) for value in DEFAULT_CHECK_CONDITIONS.get(category, ["画面を起動する"])]
    )
    base_actions = _unique_texts(
        [str(value) for value in DEFAULT_ACTIONS.get(category, ["対象処理を実行する"])]
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
        [str(value) for value in expansion_rule.get("actions", [])],
        [],
    ) or base_actions
    confirmations = _merge_text_lists(
        base_confirmations,
        [str(value) for value in expansion_rule.get("confirmation_suffix", [])],
    )

    return check_conditions, actions, confirmations


def _expand_viewpoint(viewpoint: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    category = str(viewpoint.get("category", "")).strip()
    title = str(viewpoint.get("title", "")).strip()
    viewpoint_pcl = _normalize_pcl([str(value) for value in viewpoint.get("pcl", [])])
    if category == "入力チェック":
        rules = _build_input_check_expansion_rules(viewpoint, analysis)
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
    for viewpoint in viewpoints.get("viewpoints", []):
        expanded_cases = _expand_viewpoint(viewpoint, analysis)
        for expanded_case in expanded_cases:
            test_cases.append(
                _build_testcase_from_viewpoint(
                    viewpoint=viewpoint,
                    expanded_case=expanded_case,
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