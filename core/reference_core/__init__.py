"""External reference sources and correction."""

from .screen import ScreenReference, apply_screen_reference, build_screen_reference
from .sources import ReferenceState, apply_reference_correction
from .vision import VisionDetection, apply_vision_reference, build_vision_reference

__all__ = [
    "ReferenceState",
    "ScreenReference",
    "VisionDetection",
    "apply_reference_correction",
    "apply_screen_reference",
    "apply_vision_reference",
    "build_screen_reference",
    "build_vision_reference",
]
