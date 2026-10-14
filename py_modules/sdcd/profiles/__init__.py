"""Emulated controller types."""
from .base import Battery, Encoder, Profile
from .dualsense import DualSense
from .steam import SteamController
from .switch_pro import SwitchPro
from .xbox import Xbox

PROFILES: dict[str, Profile] = {p.id: p for p in (DualSense(), DualSense(edge=True), Xbox(), SwitchPro(),
                                                  SteamController())}
DEFAULT_PROFILE = "dualsense_edge"


def profile_list() -> list[dict]:
    """The types for the frontend. usb: the type also works over a USB cable."""
    return [{"id": p.id, "label": p.label, "usb": bool(p.usb_descriptor)} for p in PROFILES.values()]


def get_profile(profile_id: str) -> Profile:
    return PROFILES.get(profile_id) or PROFILES[DEFAULT_PROFILE]
