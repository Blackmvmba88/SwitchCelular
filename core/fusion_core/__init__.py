"""Sensor fusion and orientation estimation."""

from .service import FusionFrame, fuse_orientation, fuse_samples
from .quaternion import Quaternion

__all__ = ["FusionFrame", "Quaternion", "fuse_orientation", "fuse_samples"]
