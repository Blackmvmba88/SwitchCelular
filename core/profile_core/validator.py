from __future__ import annotations

from .profile import Profile


def validate_profile(profile: Profile) -> list[str]:
    issues: list[str] = []
    if not profile.id.strip():
        issues.append("missing profile id")
    if not profile.version.strip():
        issues.append("missing profile version")
    motion = profile.motion
    sensitivity = motion.get("sensitivity", {})
    if sensitivity and not isinstance(sensitivity, dict):
        issues.append("motion.sensitivity must be a mapping")
    deadzone = motion.get("deadzone", {})
    if deadzone and not isinstance(deadzone, dict):
        issues.append("motion.deadzone must be a mapping")
    return issues


def validate_profiles(profiles: list[Profile]) -> dict[str, list[str]]:
    return {profile.id: validate_profile(profile) for profile in profiles}
