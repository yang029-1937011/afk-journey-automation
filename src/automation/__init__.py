"""AFK Journey Automation package."""

from .screenshot import screenshot_monitor
from .image_matching import findMatchings
from .click_simulation import (
    click,
    simulateClickOnImage,
    clickOnScreenShoot,
    set_language,
    get_language,
    get_asset_path,
    get_game_monitor,
    get_game_window,
)
from .game_automation import (
    autoFight,
    autoPFightFriends,
    autoFightFriends,
    autoPFight,
    FactionChallenge,
    set_stop_flag,
    stop_automation,
)

__all__ = [
    # Screenshot
    "screenshot_monitor",
    # Image matching
    "findMatchings",
    # Click simulation
    "click",
    "simulateClickOnImage",
    "clickOnScreenShoot",
    "set_language",
    "get_language",
    "get_asset_path",
    "get_game_monitor",
    "get_game_window",
    # Game automation
    "autoFight",
    "autoPFightFriends",
    "autoFightFriends",
    "autoPFight",
    "FactionChallenge",
    "set_stop_flag",
    "stop_automation",
]