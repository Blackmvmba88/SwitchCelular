# AUTO-GENERATED. DO NOT EDIT.
# protocol: blackmamba.platform.ir.v1

from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class PlatformBinding:
    protocol: str
    spec_ids: Tuple[str, ...]

PLATFORM_BINDING = PlatformBinding(
    protocol="blackmamba.platform.ir.v1",
    spec_ids=('SPEC-0000', 'SPEC-0001', 'SPEC-0002', 'SPEC-0003', 'SPEC-0004', 'SPEC-0005', 'SPEC-0006', 'SPEC-0007', 'SPEC-0008', 'SPEC-0009', 'SPEC-0010', 'SPEC-0011', 'SPEC-0012', 'SPEC-0013', 'SPEC-0014', 'SPEC-0015', 'SPEC-0016'),
)
