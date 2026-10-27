from __future__ import annotations

from dataclasses import dataclass, field
from ctypes import Structure, c_double, c_uint32, c_void_p, cdll
from typing import Protocol


class MouseBackend(Protocol):
    def move_relative(self, dx: float, dy: float) -> None: ...


class CGPoint(Structure):
    _fields_ = [("x", c_double), ("y", c_double)]


class CGEventSource(Structure):
    pass


def _load_core_graphics():
    candidates = [
        "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics",
        "/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices",
    ]
    for library in candidates:
        try:
            return cdll.LoadLibrary(library)
        except OSError:
            continue
    return None


@dataclass(slots=True)
class RelativeMouseAdapter:
    backend: MouseBackend | None = None
    emitted: list[tuple[float, float]] = field(default_factory=list)
    button_events: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.backend is None:
            self.backend = _create_core_graphics_backend()

    def initialize(self) -> None:
        return None

    def apply_motion(self, dx: float, dy: float) -> None:
        self.emitted.append((dx, dy))
        if self.backend is not None:
            self.backend.move_relative(dx, dy)

    def apply_buttons(self, buttons: int) -> None:
        self.button_events.append(buttons)
        setter = getattr(self.backend, "set_buttons", None)
        if callable(setter):
            setter(buttons)

    def flush(self) -> None:
        return None

    def shutdown(self) -> None:
        setter = getattr(self.backend, "set_buttons", None)
        if callable(setter):
            setter(0)


def _create_core_graphics_backend() -> MouseBackend | None:
    cg = _load_core_graphics()
    if cg is None:
        return None

    try:
        cg.CGEventSourceCreate.argtypes = [c_uint32]
        cg.CGEventSourceCreate.restype = c_void_p
        cg.CGEventCreate.argtypes = [c_void_p]
        cg.CGEventCreate.restype = c_void_p
        cg.CGEventGetLocation.argtypes = [c_void_p]
        cg.CGEventGetLocation.restype = CGPoint
        cg.CGEventCreateMouseEvent.argtypes = [c_void_p, c_uint32, CGPoint, c_uint32]
        cg.CGEventCreateMouseEvent.restype = c_void_p
        cg.CGEventPost.argtypes = [c_uint32, c_void_p]
        cg.CFRelease.argtypes = [c_void_p]
    except Exception:
        return None

    class CoreGraphicsMouseBackend:
        def __init__(self) -> None:
            self._buttons = 0

        def _current_location(self) -> CGPoint | None:
            probe = cg.CGEventCreate(None)
            if not probe:
                return None
            try:
                return cg.CGEventGetLocation(probe)
            finally:
                cg.CFRelease(probe)

        def _post_mouse_event(self, event_type: int, button: int, location: CGPoint) -> None:
            source = cg.CGEventSourceCreate(0)
            if not source:
                return
            event = cg.CGEventCreateMouseEvent(source, event_type, location, button)
            if event:
                cg.CGEventPost(0, event)
                cg.CFRelease(event)
            cg.CFRelease(source)

        def move_relative(self, dx: float, dy: float) -> None:
            location = self._current_location()
            if location is None:
                return
            target = CGPoint(location.x + dx, location.y + dy)
            self._post_mouse_event(5, 0, target)  # kCGEventMouseMoved

        def set_buttons(self, buttons: int) -> None:
            changed = self._buttons ^ buttons
            if changed & 0x01:
                location = self._current_location()
                if location is not None:
                    pressed = bool(buttons & 0x01)
                    self._post_mouse_event(1 if pressed else 2, 0, location)
            self._buttons = buttons

    return CoreGraphicsMouseBackend()
