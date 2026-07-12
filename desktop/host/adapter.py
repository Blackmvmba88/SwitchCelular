from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class HostAdapter(Protocol):
    def initialize(self) -> None: ...

    def apply_motion(self, dx: float, dy: float) -> None: ...

    def apply_buttons(self, buttons: int) -> None: ...

    def flush(self) -> None: ...

    def shutdown(self) -> None: ...


@dataclass(slots=True)
class HostAdapterState:
    initialized: bool = False


@dataclass(slots=True)
class MemoryHostAdapter:
    state: HostAdapterState = field(default_factory=HostAdapterState)
    motion_events: list[tuple[float, float]] = field(default_factory=list)
    button_events: list[int] = field(default_factory=list)

    def initialize(self) -> None:
        self.state.initialized = True

    def apply_motion(self, dx: float, dy: float) -> None:
        self.motion_events.append((dx, dy))

    def apply_buttons(self, buttons: int) -> None:
        self.button_events.append(buttons)

    def flush(self) -> None:
        return None

    def shutdown(self) -> None:
        self.state.initialized = False
