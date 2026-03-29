from __future__ import annotations

from typing import Any, Dict, List


def _make_viewpoint(
    vp_id: str,
    category: str,
    title: str,
    details: List[str],
    source_basis: List[str],
) -> Dict[str, Any]:
    return {
        "id": vp_id,
        "category": category,
        "title": title,
        "details": details,
        "source_basis": source_basis,
    }


def _find_controls_by_role(analysis: Dict[str, Any], role: str) -> List[Dict[str, Any]]:
    return [
        control
        for control in analysis.get("controls", [])
        if control.get("control_role") == role and control.get("test_target") is True
    ]


def _find_control_by_id(analysis: Dict[str, Any], control_id: str) -> Dict[str, Any] | None:
    for control in analysis.get("controls", []):
        if control.get("id") == control_id:
            return control
    return None


def _build_initial_display_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    has_initial_display = any(
        mode.get("mode_name") == "initial_display"
        for mode in analysis.get("screen_modes", [])
    )

    if not has_initial_display:
        return counter

    input_controls = _find_controls_by_role(analysis, "input")
    action_controls = _find_controls_by_role(analysis, "action")
    list_controls = _find_controls_by_role(analysis, "list")

    details: List[str] = []
    if input_controls:
        details.append("主要入力項目が初期表示されること")
    if action_controls:
        details.append("主要ボタンが初期表示されること")
    if list_controls:
        details.append("一覧領域が初期状態で表示されること")

    viewpoints.append(
        _make_viewpoint(
            vp_id=f"VP-{counter:03d}",
            category="初期表示",
            title="通常表示時の初期表示確認",
            details=details or ["画面が正常に初期表示されること"],
            source_basis=["screen_modes.initial_display", "controls"],
        )
    )
    return counter + 1


def _build_input_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    for control in _find_controls_by_role(analysis, "input"):
        label = control.get("label") or control.get("id")
        details = [f"{label} が入力可能であること"]

        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="入力項目",
                title=f"{label} の入力確認",
                details=details,
                source_basis=[control.get("id")],
            )
        )
        counter += 1

    return counter


def _build_length_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    for validation in analysis.get("validations", []):
        if validation.get("check_type") != "maxlength":
            continue

        target = validation.get("target")
        control = _find_control_by_id(analysis, target)
        label = (control or {}).get("label") or target
        detail = validation.get("detail") or "長さ制御あり"

        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="入力チェック",
                title=f"{label} の長さ制御確認",
                details=[f"{label} に {detail} のヒントがあること"],
                source_basis=[target, "validations.maxlength"],
            )
        )
        counter += 1

    return counter


def _build_action_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    for event in analysis.get("events", {}).get("user_actions", []):
        event_name = event.get("name") or ""
        title = f"{event_name} の処理確認"

        if event_name.endswith("_Click"):
            title = f"{event_name.replace('_Click', '')} 押下時の処理確認"
        elif event_name.endswith("_SelectedIndexChanged"):
            title = f"{event_name.replace('_SelectedIndexChanged', '')} 選択変更時の処理確認"
        elif event_name.endswith("_ItemCommand"):
            title = f"{event_name.replace('_ItemCommand', '')} 一覧操作時の処理確認"

        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="イベント",
                title=title,
                details=["イベント実行後の画面表示・処理結果が正しいこと"],
                source_basis=[event_name],
            )
        )
        counter += 1

    return counter


def _build_list_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    for control in _find_controls_by_role(analysis, "list"):
        label = control.get("label") or control.get("id")
        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="一覧表示",
                title=f"{label} の一覧表示確認",
                details=["一覧データが正しく表示されること"],
                source_basis=[control.get("id")],
            )
        )
        counter += 1

    return counter


def _build_reference_mode_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    for mode in analysis.get("screen_modes", []):
        if mode.get("mode_name") != "reference_mode":
            continue

        disable_controls = mode.get("effects", {}).get("disable_controls", [])
        if disable_controls:
            viewpoints.append(
                _make_viewpoint(
                    vp_id=f"VP-{counter:03d}",
                    category="画面モード",
                    title="参照モード時の非活性制御確認",
                    details=[
                        "参照モード時に対象コントロールが非活性となること",
                        f"対象コントロール数: {len(disable_controls)}",
                    ],
                    source_basis=["screen_modes.reference_mode"],
                )
            )
            counter += 1

    return counter


def _build_concurrency_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    has_concurrency_hint = any(
        validation.get("check_type") == "concurrency_check_hint"
        for validation in analysis.get("validations", [])
    )

    if has_concurrency_hint:
        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="排他制御",
                title="更新時の排他チェック確認",
                details=["更新時に排他制御が実施されること"],
                source_basis=["validations.concurrency_check_hint"],
            )
        )
        counter += 1

    return counter


def generate_viewpoints(analysis: Dict[str, Any]) -> Dict[str, Any]:
    viewpoints: List[Dict[str, Any]] = []
    counter = 1

    counter = _build_initial_display_viewpoints(analysis, viewpoints, counter)
    counter = _build_input_viewpoints(analysis, viewpoints, counter)
    counter = _build_length_viewpoints(analysis, viewpoints, counter)
    counter = _build_action_viewpoints(analysis, viewpoints, counter)
    counter = _build_list_viewpoints(analysis, viewpoints, counter)
    counter = _build_reference_mode_viewpoints(analysis, viewpoints, counter)
    counter = _build_concurrency_viewpoints(analysis, viewpoints, counter)

    return {
        "screen_id": analysis.get("screen_id"),
        "screen_name": analysis.get("screen_name"),
        "viewpoints": viewpoints,
        "summary": {
            "viewpoint_count": len(viewpoints),
        },
    }