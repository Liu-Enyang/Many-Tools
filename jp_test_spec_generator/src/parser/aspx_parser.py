from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup


ASP_CONTROL_TYPES = {
    "asp:textbox": "TextBox",
    "asp:button": "Button",
    "asp:label": "Label",
    "asp:dropdownlist": "DropDownList",
    "asp:radiobuttonlist": "RadioButtonList",
    "asp:hiddenfield": "HiddenField",
    "asp:linkbutton": "LinkButton",
    "asp:checkbox": "CheckBox",
    "asp:repeater": "Repeater",
}


def _normalize_attr(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, list):
        return " ".join(str(x) for x in value)
    return str(value).strip()


def _tag_name(tag) -> str:
    return getattr(tag, "name", "").lower()


def _extract_control(tag) -> Dict[str, Any] | None:
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


def _extract_table_headers(soup: BeautifulSoup) -> List[str]:
    headers: List[str] = []
    for th in soup.find_all("th"):
        text = th.get_text(" ", strip=True)
        if text:
            headers.append(text)
    return headers


def parse_aspx(file_path: str | Path) -> Dict[str, Any]:
    path = Path(file_path)
    content = path.read_text(encoding="utf-8", errors="ignore")

    soup = BeautifulSoup(content, "lxml-xml")
    if soup is None or not soup.find():
        # fallback
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

    for control in controls:
        control["label"] = label_map.get(control["id"])

    page_match = re.search(r'Inherits="([^"]+)"', content, re.IGNORECASE)
    codebehind_match = re.search(r'CodeBehind="([^"]+)"', content, re.IGNORECASE)

    return {
        "file": str(path),
        "page_inherits": page_match.group(1) if page_match else None,
        "codebehind": codebehind_match.group(1) if codebehind_match else None,
        "controls": controls,
        "table_headers": _extract_table_headers(soup),
        "raw_summary": {
            "control_count": len(controls),
        },
    }