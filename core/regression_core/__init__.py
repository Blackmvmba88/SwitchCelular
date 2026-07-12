"""Capture, playback, and regression comparison."""

from .recorder import MotionTrace, finalize_trace, record_stage, write_trace

__all__ = ["MotionTrace", "finalize_trace", "record_stage", "write_trace"]
