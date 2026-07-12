from __future__ import annotations

from pathlib import Path

import yaml

from .profile import Profile


class ProfileLoadError(ValueError):
    pass


REQUIRED_KEYS = ["id", "version"]


def load_profiles(directory: Path) -> list[Profile]:
    if not directory.exists():
        return []
    profiles = []
    for path in sorted(directory.glob("*.yaml")):
        profiles.append(load_profile(path))
    return profiles


def load_profile_by_id(directory: Path, profile_id: str) -> Profile:
    for profile in load_profiles(directory):
        if profile.id == profile_id:
            return profile
    raise ProfileLoadError(f"{profile_id}: profile not found in {directory}")


def load_profile(path: Path) -> Profile:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ProfileLoadError(f"{path.name}: missing keys: {', '.join(missing)}")
    return Profile(
        id=str(data["id"]),
        version=str(data["version"]),
        device=dict(data.get("device", {})),
        motion=dict(data.get("motion", {})),
        trigger=dict(data.get("trigger", {})),
        smoothing=dict(data.get("smoothing", {})),
        mapping=dict(data.get("mapping", {})),
        limits=dict(data.get("limits", {})),
        reference=dict(data.get("reference", {})),
        context=dict(data.get("context", {})),
    )
