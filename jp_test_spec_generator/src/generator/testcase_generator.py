from __future__ import annotations

from typing import Any, Dict, List


def _make_testcase(
    case_id: str,
    category: str,
    viewpoint_id: str,
    viewpoint_title: str,
    precondition: str,
    input_conditions: List[Dict[str, Any]],
    operation: List[str],
    expected_result: List[str],
    source_basis: List[str],
) -> Dict[str, Any]:
    return {
        "case_id": case_id,
        "category": category,
        "test_viewpoint_id": viewpoint_id,
        "test_viewpoint": viewpoint_title,
        "precondition": precondition,
        "input_conditions": input_conditions,
        "operation": operation,
        "expected_result": expected_result,
        "source_basis": source_basis,
    }


def _build_testcase_from_viewpoint(viewpoint: Dict[str, Any], index: int) -> Dict[str, Any]:
    case_id = f"TC-{index:03d}"
    category = viewpoint.get("category", "")
    viewpoint_id = viewpoint.get("id", "")
    viewpoint_title = viewpoint.get("title", "")
    details = viewpoint.get("details", [])
    source_basis = [viewpoint_id] + viewpoint.get("source_basis", [])

    if category == "初期表示":
        return _make_testcase(
            case_id=case_id,
            category=category,
            viewpoint_id=viewpoint_id,
            viewpoint_title=viewpoint_title,
            precondition="通常モードで画面を起動する",
            input_conditions=[],
            operation=["画面を起動する"],
            expected_result=details or ["画面が正常に初期表示されること"],
            source_basis=source_basis,
        )

    if category == "入力項目":
        return _make_testcase(
            case_id=case_id,
            category=category,
            viewpoint_id=viewpoint_id,
            viewpoint_title=viewpoint_title,
            precondition="通常モードで画面を起動する",
            input_conditions=[],
            operation=["対象項目を確認する"],
            expected_result=details or ["対象項目が入力可能であること"],
            source_basis=source_basis,
        )

    if category == "入力チェック":
        return _make_testcase(
            case_id=case_id,
            category=category,
            viewpoint_id=viewpoint_id,
            viewpoint_title=viewpoint_title,
            precondition="通常モードで画面を起動する",
            input_conditions=[],
            operation=["対象項目に規定外の値を入力する"],
            expected_result=details or ["入力チェックが正しく行われること"],
            source_basis=source_basis,
        )

    if category == "イベント":
        return _make_testcase(
            case_id=case_id,
            category=category,
            viewpoint_id=viewpoint_id,
            viewpoint_title=viewpoint_title,
            precondition="通常モードで画面を起動する",
            input_conditions=[],
            operation=["対象イベントを実行する"],
            expected_result=details or ["イベント実行後の処理結果が正しいこと"],
            source_basis=source_basis,
        )

    if category == "一覧表示":
        return _make_testcase(
            case_id=case_id,
            category=category,
            viewpoint_id=viewpoint_id,
            viewpoint_title=viewpoint_title,
            precondition="一覧表示対象データが存在する状態で画面を起動する",
            input_conditions=[],
            operation=["画面を起動する"],
            expected_result=details or ["一覧データが正しく表示されること"],
            source_basis=source_basis,
        )

    if category == "画面モード":
        return _make_testcase(
            case_id=case_id,
            category=category,
            viewpoint_id=viewpoint_id,
            viewpoint_title=viewpoint_title,
            precondition="参照モードで画面を起動する",
            input_conditions=[],
            operation=["画面を起動する"],
            expected_result=details or ["参照モード時の制御が正しいこと"],
            source_basis=source_basis,
        )

    if category == "排他制御":
        return _make_testcase(
            case_id=case_id,
            category=category,
            viewpoint_id=viewpoint_id,
            viewpoint_title=viewpoint_title,
            precondition="対象データが更新済みの状態で更新処理を実行する",
            input_conditions=[],
            operation=["更新処理を実行する"],
            expected_result=details or ["排他制御が正しく行われること"],
            source_basis=source_basis,
        )

    return _make_testcase(
        case_id=case_id,
        category=category,
        viewpoint_id=viewpoint_id,
        viewpoint_title=viewpoint_title,
        precondition="画面を起動する",
        input_conditions=[],
        operation=["対象処理を実行する"],
        expected_result=details or ["期待結果が正しいこと"],
        source_basis=source_basis,
    )


def generate_testcases(
    analysis: Dict[str, Any],
    viewpoints: Dict[str, Any],
) -> Dict[str, Any]:
    test_cases: List[Dict[str, Any]] = []

    for index, viewpoint in enumerate(viewpoints.get("viewpoints", []), start=1):
        test_cases.append(_build_testcase_from_viewpoint(viewpoint, index))

    return {
        "screen_id": analysis.get("screen_id"),
        "screen_name": analysis.get("screen_name"),
        "test_cases": test_cases,
        "summary": {
            "test_case_count": len(test_cases),
        },
    }