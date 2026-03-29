from __future__ import annotations

from typing import Any, Dict, List, Tuple


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


def _build_case_items(viewpoint: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
    category = str(viewpoint.get("category", "")).strip()
    details = viewpoint.get("details", [])
    detail_texts = _unique_texts([str(detail) for detail in details])

    check_conditions = _unique_texts(
        [str(value) for value in DEFAULT_CHECK_CONDITIONS.get(category, ["画面を起動する"])]
    )
    actions = _unique_texts(
        [str(value) for value in DEFAULT_ACTIONS.get(category, ["対象処理を実行する"])]
    )
    confirmations = _unique_texts(
        detail_texts or DEFAULT_CONFIRMATIONS.get(category, ["期待結果が正しいこと"])
    )

    return check_conditions, actions, confirmations


def _build_testcase_from_viewpoint(
    viewpoint: Dict[str, Any],
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
    viewpoint_title = str(viewpoint.get("title", "")).strip()
    source_basis = _unique_texts([viewpoint_id] + [str(value) for value in viewpoint.get("source_basis", [])])

    check_conditions, actions, confirmations = _build_case_items(viewpoint)

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

    for index, viewpoint in enumerate(viewpoints.get("viewpoints", []), start=1):
        test_cases.append(
            _build_testcase_from_viewpoint(
                viewpoint=viewpoint,
                index=index,
                check_condition_registry=check_condition_registry,
                check_condition_definitions=check_condition_definitions,
                action_registry=action_registry,
                action_definitions=action_definitions,
                confirmation_registry=confirmation_registry,
                confirmation_definitions=confirmation_definitions,
            )
        )

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
            "check_condition_count": len(check_condition_definitions),
            "action_count": len(action_definitions),
            "confirmation_count": len(confirmation_definitions),
        },
    }