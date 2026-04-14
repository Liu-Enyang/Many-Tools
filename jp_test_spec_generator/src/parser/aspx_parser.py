from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup


ASP_CONTROL_TYPES = {
    "asp:textbox": "TextBox",
    "asp:button": "Button",
    "asp:label": "Label",
    "asp:dropdownlist": "DropDownList",
    "asp:radiobuttonlist": "RadioButtonList",
    "asp:radiobutton": "RadioButton",
    "asp:hiddenfield": "HiddenField",
    "asp:linkbutton": "LinkButton",
    "asp:checkbox": "CheckBox",
    "asp:repeater": "Repeater",
}

TITLE_CLASS_CANDIDATES = {
    "title",
    "page-title",
    "screen-title",
    "main-title",
}


def _normalize_attr(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, list):
        return " ".join(str(x) for x in value)
    return str(value).strip()


def _tag_name(tag) -> str:
    return getattr(tag, "name", "").lower()


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _extract_control(tag) -> Optional[Dict[str, Any]]:
    name = _tag_name(tag)

    if name in ASP_CONTROL_TYPES:
        attrs = {k: _normalize_attr(v) for k, v in tag.attrs.items()}
        control_id = attrs.get("id")
        if not control_id:
            return None

        return {
            "id": control_id,
            "type": ASP_CONTROL_TYPES[name],
            "runat": attrs.get("runat"),
            "text": attrs.get("text"),
            "maxlength": attrs.get("maxlength") or attrs.get("data-maxlength"),
            "css_class": attrs.get("cssclass") or attrs.get("class"),
            "on_click": attrs.get("onclick"),
            "on_selected_index_changed": attrs.get("onselectedindexchanged"),
            "client_id_mode": attrs.get("clientidmode"),
            "required": "required" in tag.attrs,
            "data_type": attrs.get("data-type"),
            "input_min": attrs.get("min"),
            "input_max": attrs.get("max"),
            "data_scale": attrs.get("data-scale"),
            "group_name": attrs.get("groupname"),
            "raw_attributes": attrs,
        }

    if name == "input":
        attrs = {k: _normalize_attr(v) for k, v in tag.attrs.items()}
        input_type = (attrs.get("type") or "").lower()
        if input_type == "button":
            return {
                "id": attrs.get("id", ""),
                "type": "HtmlButton",
                "runat": attrs.get("runat"),
                "text": attrs.get("value"),
                "maxlength": attrs.get("maxlength"),
                "css_class": attrs.get("class"),
                "on_click": attrs.get("onclick"),
                "on_selected_index_changed": None,
                "client_id_mode": None,
                "required": "required" in tag.attrs,
                "data_type": None,
                "input_min": None,
                "input_max": None,
                "data_scale": None,
                "group_name": None,
                "raw_attributes": attrs,
            }

    # カスタム名前空間のConfirmButton（cc1:ConfirmButton, cc3:ConfirmButton など）
    if re.match(r'^cc\d+:confirmbutton$', name) or re.match(r'^cc\d+:\w*button$', name):
        attrs = {k: _normalize_attr(v) for k, v in tag.attrs.items()}
        control_id = attrs.get("id")
        if not control_id:
            return None
        return {
            "id": control_id,
            "type": "ConfirmButton",
            "runat": attrs.get("runat"),
            "text": attrs.get("text") or attrs.get("value"),
            "maxlength": None,
            "css_class": attrs.get("cssclass") or attrs.get("class"),
            "on_click": attrs.get("onclick"),
            "on_selected_index_changed": None,
            "client_id_mode": attrs.get("clientidmode"),
            "required": False,
            "data_type": None,
            "input_min": None,
            "input_max": None,
            "data_scale": None,
            "group_name": None,
            "raw_attributes": attrs,
        }

    return None


def _extract_labels(soup: BeautifulSoup) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for label in soup.find_all("label"):
        target = label.get("for")
        text = label.get_text(" ", strip=True)
        if target and text:
            result[target] = text
    return result


def _extract_required_from_labels(soup: BeautifulSoup) -> set:
    """<label for="..." data-required> を持つ control_id を返す"""
    required_ids: set = set()
    for label in soup.find_all("label"):
        if "data-required" in label.attrs:
            target = label.get("for")
            if target:
                required_ids.add(target)
    return required_ids


def _extract_table_headers(soup: BeautifulSoup) -> List[str]:
    headers: List[str] = []
    for th in soup.find_all("th"):
        text = th.get_text(" ", strip=True)
        if text:
            headers.append(text)
    return headers


def _extract_title_candidates(soup: BeautifulSoup) -> List[Dict[str, str]]:
    candidates: List[Dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for tag in soup.find_all(True):
        tag_name = _tag_name(tag)
        css_class = _normalize_attr(tag.get("class")) or ""
        text = tag.get_text(" ", strip=True)

        if not text:
            continue

        normalized_class = css_class.lower()
        is_title_tag = tag_name in {"h1", "h2", "h3"}
        is_title_class = any(cls in normalized_class.split() for cls in TITLE_CLASS_CANDIDATES)

        if not is_title_tag and not is_title_class:
            continue

        key = (tag_name, text)
        if key in seen:
            continue
        seen.add(key)

        candidates.append({
            "tag": tag_name,
            "text": text,
            "css_class": css_class,
        })

    return candidates


def _attach_nearest_header_labels(controls: List[Dict[str, Any]], soup: BeautifulSoup) -> None:
    control_by_id = {control.get("id"): control for control in controls if control.get("id")}

    for tr in soup.find_all("tr"):
        current_header: Optional[str] = None
        for cell in tr.children:
            cell_name = getattr(cell, "name", None)
            if cell_name is None:
                continue
            if cell_name == "th":
                header_text = cell.get_text(" ", strip=True)
                current_header = header_text if header_text else current_header
            elif cell_name == "td" and current_header:
                for tag in cell.find_all(True):
                    control_id = tag.get("id")
                    if control_id and control_id in control_by_id:
                        if not control_by_id[control_id].get("label"):
                            control_by_id[control_id]["label"] = current_header


def parse_aspx(file_path: str | Path) -> Dict[str, Any]:
    path = Path(file_path)
    content = path.read_text(encoding="utf-8", errors="ignore")

    soup = BeautifulSoup(content, "lxml-xml")
    if soup is None or not soup.find():
        soup = BeautifulSoup(content, "lxml")

    controls: List[Dict[str, Any]] = []
    seen_ids = set()

    for tag in soup.find_all(True):
        control = _extract_control(tag)
        if not control:
            continue

        control_id = control.get("id")
        if not control_id or control_id in seen_ids:
            continue

        seen_ids.add(control_id)
        controls.append(control)

    label_map = _extract_labels(soup)
    required_ids = _extract_required_from_labels(soup)

    for control in controls:
        control["label"] = label_map.get(control["id"])
        if not control.get("required") and control["id"] in required_ids:
            control["required"] = True

    _attach_nearest_header_labels(controls, soup)

    page_match = re.search(r'Inherits="([^"]+)"', content, re.IGNORECASE)
    codebehind_match = re.search(r'CodeBehind="([^"]+)"', content, re.IGNORECASE)

    return {
        "file": str(path),
        "page_inherits": page_match.group(1) if page_match else None,
        "codebehind": codebehind_match.group(1) if codebehind_match else None,
        "controls": controls,
        "table_headers": _extract_table_headers(soup),
        "title_candidates": _extract_title_candidates(soup),
        "raw_summary": {
            "control_count": len(controls),
        },
    }