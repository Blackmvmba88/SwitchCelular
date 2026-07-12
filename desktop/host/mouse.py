from __future__ import annotations

from dataclasses import dataclass, field
from ctypes import Structure, c_double, c_int64, c_uint32, c_void_p, cdll
from ctypes import POINTER
from typing import Callable, Protocol


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
        return None

    def flush(self) -> None:
        return None

    def shutdown(self) -> None:
        return None


def _create_core_graphics_backend() -> MouseBackend | None:
    cg = _load_core_graphics()
    if cg is None:
        return None

    try:
        cg.CGEventSourceCreate.argtypes = [c_uint32]
        cg.CGEventSourceCreate.restype = c_void_p
        cg.CGEventCreateMouseEvent.argtypes = [c_void_p, c_uint32, CGPoint, c_uint32]
        cg.CGEventCreateMouseEvent.restype = c_void_p
        cg.CGEventSetIntegerValueField.argtypes = [c_void_p, c_uint32, c_int64]
        cg.CGEventPost.argtypes = [c_uint32, c_void_p]
        cg.CFRelease.argtypes = [c_void_p]
    except Exception:
        return None

    class CoreGraphicsMouseBackend:
        def move_relative(self, dx: float, dy: float) -> None:
            source = cg.CGEventSourceCreate(0)
            if not source:
                return None
            event = cg.CGEventCreateMouseEvent(source, 5, CGPoint(0.0, 0.0), 0)
            if not event:
                cg.CFRelease(source)
                return None
            cg.CGEventSetIntegerValueField(event, 93, int(round(dx)))
            cg.CGEventSetIntegerValueField(event, 94, int(round(dy)))
            cg.CGEventPost(0, event)
            cg.CFRelease(event)
            cg.CFRelease(source)

    return CoreGraphicsMouseBackend()
