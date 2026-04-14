from __future__ import annotations

from typing import Any, Dict, List


def _detect_pcl(category: str, title: str, details: List[str]) -> List[str]:
    text = f"{category} {title} {' '.join(details)}"
    pcl = set()

    # Normal (N)
    if any(k in text for k in ["正常", "初期表示", "表示", "一覧"]):
        pcl.add("N")

    # Error (E)
    if any(k in text for k in ["エラー", "異常", "チェック", "制御"]):
        pcl.add("E")

    # Limit/Boundary (L)
    if any(k in text for k in ["桁", "以上", "以下", "最大", "最小", "長さ"]):
        pcl.add("L")

    # Interface (I)
    if any(k in text for k in ["API", "連携", "DB", "インタフェース"]):
        pcl.add("I")

    # default
    return sorted(pcl) if pcl else ["N"]

def _make_viewpoint(
    vp_id: str,
    category: str,
    title: str,
    details: List[str],
    source_basis: List[str],
) -> Dict[str, Any]:
    pcl = _detect_pcl(category, title, details)

    return {
        "id": vp_id,
        "category": category,
        "title": title,
        "details": details,
        "pcl": pcl,
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
                details=[f"{label} に {detail} の入力チェックがあること"],
                source_basis=[target, "validations.maxlength"],
            )
        )
        counter += 1

    return counter

def _build_blur_validation_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    for target in analysis.get("blur_validation_targets", []):
        label = target.get("label") or target.get("target") or "対象項目"
        max_length = target.get("max_length")
        trigger = target.get("trigger") or "blur"

        if not max_length:
            continue

        trigger_text = "フォーカスアウト時" if trigger == "blur" else "入力時"

        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="入力チェック",
                title=f"{label} の{trigger_text}桁数チェック確認",
                details=[
                    f"{label} に最大桁数以内の値を入力して{trigger_text}にエラーとならないこと",
                    f"{label} に最大桁数超過の値を入力して{trigger_text}にエラーメッセージが表示されること",
                ],
                source_basis=target.get("source_basis", []) or [target.get("target") or "blur_validation"],
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


def _build_range_validation_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    for control in analysis.get("controls", []):
        if control.get("control_role") != "input" or not control.get("test_target"):
            continue

        data_type = (control.get("data_type") or "").strip()
        input_min = control.get("input_min")
        input_max = control.get("input_max")

        if not data_type and input_min is None and input_max is None:
            continue

        label = control.get("label") or control.get("id")
        control_id = control.get("id")
        details = []

        TYPE_LABELS = {
            "money": "金額（数値）",
            "decimal": "数値",
            "numeric": "数値",
        }
        if data_type:
            type_label = TYPE_LABELS.get(data_type, data_type)
            details.append(f"{label} は{type_label}形式で入力すること")
        if input_min is not None and input_max is not None:
            details.append(f"{label} の入力範囲は {input_min} ～ {input_max} であること")
        elif input_min is not None:
            details.append(f"{label} の最小値は {input_min} であること")
        elif input_max is not None:
            details.append(f"{label} の最大値は {input_max} であること")

        if not details:
            continue

        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="入力チェック",
                title=f"{label} の入力値チェック確認",
                details=details,
                source_basis=[control_id, "aspx.data-type", "aspx.min", "aspx.max"],
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

def _collect_sort_target_lists(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    list_controls = _find_controls_by_role(analysis, "list")
    results: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()

    for control in list_controls:
        control_id = str(control.get("id") or "").strip()
        if not control_id or control_id in seen_ids:
            continue
        seen_ids.add(control_id)
        results.append(control)

    return results

def _build_javascript_event_handler_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    javascript_analysis = analysis.get("javascript_analysis", {}) or {}

    for item in javascript_analysis.get("event_handlers", []):
        title = str(item.get("title") or "").strip()
        detail = str(item.get("detail") or "").strip()
        source_basis = list(item.get("source_basis", []) or [])

        if "顧客クリアボタン押下時制御あり" in title:
            viewpoints.append(
                _make_viewpoint(
                    vp_id=f"VP-{counter:03d}",
                    category="イベント",
                    title="顧客クリアボタン押下時の項目クリア確認",
                    details=[
                        "顧客クリアボタン押下時に顧客番号がクリアされること",
                        "顧客クリアボタン押下時に顧客名がクリアされること",
                    ],
                    source_basis=source_basis or ["controls.btnClear", "js.click.clear_customer_fields"],
                )
            )
            counter += 1
            continue

        if "概況クリアボタン押下時制御あり" in title:
            viewpoints.append(
                _make_viewpoint(
                    vp_id=f"VP-{counter:03d}",
                    category="イベント",
                    title="概況クリアボタン押下時のテキストエリアクリア確認",
                    details=[
                        "概況クリアボタン押下時に事故及び延滞に至った原因がクリアされること",
                        "概況クリアボタン押下時に債務者および保証人の現況がクリアされること",
                        "概況クリアボタン押下時に回収、解消の方針、スケジュールがクリアされること",
                        "概況クリアボタン押下時に備考、特記事項がクリアされること",
                    ],
                    source_basis=source_basis or ["controls.btnSummaryClear", "js.click.clear_summary_fields"],
                )
            )
            counter += 1
            continue

        if "顧客検索ボタン押下時制御あり" in title:
            viewpoints.append(
                _make_viewpoint(
                    vp_id=f"VP-{counter:03d}",
                    category="イベント",
                    title="顧客検索ボタン押下時の前提条件・検索結果反映確認",
                    details=[
                        "顧客検索ボタン押下時に店番未選択の場合はエラーメッセージが表示されること",
                        "顧客検索ボタン押下時に正常時は顧客検索ダイアログが起動すること",
                        "顧客選択後に顧客番号および顧客名が画面へ反映されること",
                    ],
                    source_basis=source_basis or ["controls.btnCustSearch", "js.click.customer_search"],
                )
            )
            counter += 1
            continue

        if "帳票ダウンロードボタン押下時制御あり" in title:
            viewpoints.append(
                _make_viewpoint(
                    vp_id=f"VP-{counter:03d}",
                    category="イベント",
                    title="帳票ダウンロードボタン押下時の前提条件確認",
                    details=[
                        "帳票ダウンロードボタン押下時に顧客番号未入力の場合はエラーメッセージが表示されること",
                        "帳票ダウンロードボタン押下時に店番未選択の場合はエラーメッセージが表示されること",
                        "帳票ダウンロードボタン押下時に帳票未選択の場合はエラーメッセージが表示されること",
                        "帳票ダウンロードボタン押下時に正常時はダウンロード処理が実行されること",
                    ],
                    source_basis=source_basis or ["controls.btnDownload", "js.click.download"],
                )
            )
            counter += 1
            continue

        if title:
            viewpoints.append(
                _make_viewpoint(
                    vp_id=f"VP-{counter:03d}",
                    category="イベント",
                    title=title.replace("制御あり", "確認") if "制御あり" in title else f"{title}確認",
                    details=[detail or "JavaScriptイベント処理結果が正しいこと"],
                    source_basis=source_basis or ["javascript.event_handlers"],
                )
            )
            counter += 1

    return counter


def _build_javascript_viewpoints(
    analysis: Dict[str, Any],
    viewpoints: List[Dict[str, Any]],
    counter: int,
) -> int:
    javascript_analysis = analysis.get("javascript_analysis", {}) or {}

    def _collect_sources(key: str) -> List[str]:
        sources: List[str] = []
        for item in javascript_analysis.get(key, []):
            path = item.get("relative_path") or item.get("file_name") or "javascript"
            if path not in sources:
                sources.append(path)
        return sources

    counter = _build_javascript_event_handler_viewpoints(analysis, viewpoints, counter)

    if javascript_analysis.get("screen_controls"):
        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="画面モード",
                title="参照モード時のJavaScript制御確認",
                details=[
                    "参照モード時に入力項目・ボタン・リンクが操作不可となること",
                    "参照モード時に子要素も含めて非活性制御されること",
                ],
                source_basis=_collect_sources("screen_controls"),
            )
        )
        counter += 1

    if javascript_analysis.get("validation_related"):
        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="入力チェック",
                title="JavaScript入力チェック・エラーメッセージ確認",
                details=[
                    "未入力時にエラーメッセージが表示されること",
                    "入力条件不備時に処理が中断されること",
                ],
                source_basis=_collect_sources("validation_related"),
            )
        )
        counter += 1

    if javascript_analysis.get("download_related"):
        viewpoints.append(
            _make_viewpoint(
                vp_id=f"VP-{counter:03d}",
                category="イベント",
                title="帳票ダウンロード前提チェック確認",
                details=[
                    "帳票未選択時にエラーメッセージが表示されること",
                    "顧客番号・店番未設定時にダウンロード実行されないこと",
                ],
                source_basis=_collect_sources("download_related"),
            )
        )
        counter += 1

    if javascript_analysis.get("sort_related"):
        sort_sources = _collect_sources("sort_related")
        sort_target_lists = _collect_sort_target_lists(analysis)

        if sort_target_lists:
            for control in sort_target_lists:
                label = control.get("label") or control.get("id") or "一覧"
                control_id = control.get("id") or "list"
                viewpoints.append(
                    _make_viewpoint(
                        vp_id=f"VP-{counter:03d}",
                        category="一覧表示",
                        title=f"{label} のソート処理確認",
                        details=[
                            f"{label}のヘッダ押下時に昇順・降順が切り替わること",
                            f"{label}で文字列・数値・日付が指定種別で正しくソートされること",
                        ],
                        source_basis=sort_sources + [f"controls.{control_id}"],
                    )
                )
                counter += 1
        else:
            viewpoints.append(
                _make_viewpoint(
                    vp_id=f"VP-{counter:03d}",
                    category="一覧表示",
                    title="一覧ソート処理確認",
                    details=[
                        "一覧ヘッダ押下時に昇順・降順が切り替わること",
                        "文字列・数値・日付が指定種別で正しくソートされること",
                    ],
                    source_basis=sort_sources,
                )
            )
            counter += 1

    return counter

def generate_viewpoints(analysis: Dict[str, Any]) -> Dict[str, Any]:
    viewpoints: List[Dict[str, Any]] = []
    counter = 1

    counter = _build_initial_display_viewpoints(analysis, viewpoints, counter)
    counter = _build_input_viewpoints(analysis, viewpoints, counter)
    counter = _build_range_validation_viewpoints(analysis, viewpoints, counter)
    counter = _build_length_viewpoints(analysis, viewpoints, counter)
    counter = _build_blur_validation_viewpoints(analysis, viewpoints, counter)
    counter = _build_action_viewpoints(analysis, viewpoints, counter)
    counter = _build_list_viewpoints(analysis, viewpoints, counter)
    counter = _build_reference_mode_viewpoints(analysis, viewpoints, counter)
    counter = _build_concurrency_viewpoints(analysis, viewpoints, counter)
    counter = _build_javascript_viewpoints(analysis, viewpoints, counter)

    javascript_analysis = analysis.get("javascript_analysis", {}) or {}
    blur_validation_targets = analysis.get("blur_validation_targets", []) or []

    return {
        "screen_id": analysis.get("screen_id"),
        "screen_name": analysis.get("screen_name"),
        "viewpoints": viewpoints,
        "summary": {
            "viewpoint_count": len(viewpoints),
            "javascript_viewpoint_source_count": sum(len(v) for v in javascript_analysis.values()) if javascript_analysis else 0,
            "blur_validation_viewpoint_source_count": len(blur_validation_targets),
        },
    }