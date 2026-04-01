from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional


@dataclass
class Control:
    id: str
    type: str
    runat: Optional[str] = None
    text: Optional[str] = None
    maxlength: Optional[str] = None
    css_class: Optional[str] = None
    on_click: Optional[str] = None
    on_selected_index_changed: Optional[str] = None
    client_id_mode: Optional[str] = None
    required: bool = False
    raw_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventMethod:
    name: str
    event_type: str
    related_controls: List[str] = field(default_factory=list)


@dataclass
class ValidationHint:
    check_type: str
    target: Optional[str] = None
    detail: Optional[str] = None
    source: Optional[str] = None


@dataclass
class ScreenModeHint:
    mode_name: str
    detail: str
    source: Optional[str] = None


@dataclass
class AnalysisResult:
    screen_id: str
    screen_name: str
    sources: Dict[str, str]
    controls: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    validations: List[Dict[str, Any]]
    screen_modes: List[Dict[str, Any]]
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)